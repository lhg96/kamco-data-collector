"""
KAMCO Public Auction Data Collection Web Application

Usage:
  python web/app.py

Environment Variables (.env):
  KAMCO_API_KEY - KAMCO API service key
  MONGO_URI - MongoDB connection URI (default: mongodb://localhost:27017)
  FLASK_SECRET_KEY - Flask secret key
  FLASK_PORT - Flask port (default: 5000)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.kamco_collector_service import KamcoCollectorService
from rag.query import smart_search, generate_answer

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())

# MongoDB 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "kamco")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "collected_items")

# MongoDB 클라이언트
mongo_client = None
db = None
collection = None


def init_mongodb():
    """MongoDB 연결 초기화"""
    global mongo_client, db, collection
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        db = mongo_client[MONGO_DB_NAME]
        collection = db[MONGO_COLLECTION_NAME]
        return True
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")
        return False


@app.route('/')
def index():
    """홈 페이지 (대시보드)"""
    if collection is None:
        return render_template('error.html', message="MongoDB 연결이 필요합니다.")
    
    try:
        # 통계 정보
        total_count = collection.count_documents({})
        recent_count = collection.count_documents({
            "collected_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        # 최근 수집 데이터
        recent_items = list(collection.find().sort("collected_at", DESCENDING).limit(5))
        
        stats = {
            "total_count": total_count,
            "recent_count": recent_count,
            "recent_items": recent_items
        }
        
        return render_template('index.html', stats=stats)
    except Exception as e:
        return render_template('error.html', message=f"데이터 조회 실패: {e}")


@app.route('/collect')
def collect_page():
    """수집 관리 페이지"""
    return render_template('collect.html')


@app.route('/api/collect', methods=['POST'])
def api_collect():
    """데이터 수집 API"""
    try:
        collect_mode = request.form.get('collect_mode', 'list')
        
        service = KamcoCollectorService(
            db_name=MONGO_DB_NAME,
            collection_name=MONGO_COLLECTION_NAME
        )
        
        if not service.connect_mongodb():
            return jsonify({'success': False, 'message': 'MongoDB 연결 실패'}), 500
        
        stats = {}
        
        if collect_mode == 'latest':
            days = int(request.form.get('days', 30))
            num_of_rows = int(request.form.get('num_of_rows', 50))
            prpt_dvsn_cd = request.form.get('prpt_dvsn_cd', '0001')
            
            stats = service.run(
                num_of_rows=num_of_rows,
                prpt_dvsn_cd=prpt_dvsn_cd,
                save_to_db=True,
                use_latest=True,
                days=days
            )
        else:
            page_no = int(request.form.get('page_no', 1))
            num_of_rows = int(request.form.get('num_of_rows', 10))
            prpt_dvsn_cd = request.form.get('prpt_dvsn_cd', '0001')
            
            stats = service.run(
                page_no=page_no,
                num_of_rows=num_of_rows,
                prpt_dvsn_cd=prpt_dvsn_cd,
                save_to_db=True,
                use_latest=False
            )
        
        if stats is None:
             stats = {"saved_items": 0}

        # Auto Normalize & Embed if data saved
        if stats.get("saved_items", 0) > 0:
            try:
                from normalize.kamco_normalizer import normalize
                from rag.embed import embed
                
                stats['normalized_count'] = normalize()
                
                try:
                    stats['embedded_count'] = embed()
                    stats['rag_ready'] = True
                except Exception as e:
                    stats['rag_ready'] = False
                    stats['embed_error'] = str(e)
            except Exception as e:
                stats['process_error'] = str(e)
        
        msg = f'{stats.get("saved_items", 0)}개 수집 완료.'
        if stats.get('rag_ready'):
            msg += f' (임베딩 완료)'
            
        return jsonify({'success': True, 'stats': stats, 'message': msg})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'수집 실패: {str(e)}'}), 500


@app.route('/list')
def list_page():
    """수집 리스트 게시판"""
    if collection is None:
        return render_template('error.html', message="MongoDB 연결이 필요합니다.")
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search_query = request.args.get('q', '')
        
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"PLNM_NO": {"$regex": search_query, "$options": "i"}},
                    {"PBCT_NO": {"$regex": search_query, "$options": "i"}},
                    {"basic_info.PLNM_NM": {"$regex": search_query, "$options": "i"}}, # Check path
                    {"announce_list_item.PLNM_NM": {"$regex": search_query, "$options": "i"}},
                ]
            }
        
        total_count = collection.count_documents(query)
        skip = (page - 1) * per_page
        
        # Sort by PLNM_NO desc
        items = list(collection.find(query).sort([("PLNM_NO", DESCENDING)]).skip(skip).limit(per_page))
        
        total_pages = (total_count + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1,
            'next_page': page + 1,
        }
        
        return render_template('list.html', items=items, pagination=pagination, search_query=search_query)
        
    except Exception as e:
        return render_template('error.html', message=f"데이터 조회 실패: {e}")


@app.route('/detail/<item_id>')
def detail_page(item_id):
    """상 상세 보기 페이지"""
    if collection is None:
        return render_template('error.html', message="MongoDB 연결이 필요합니다.")
    
    try:
        item = collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            return render_template('error.html', message="데이터를 찾을 수 없습니다.")
        
        # Remove duplicate files if any
        if item.get('file_info'):
            seen = set()
            unique_files = []
            for file in item['file_info']:
                fid = file.get('ATCH_FILE_PTCS_NO')
                if fid and fid not in seen:
                    seen.add(fid)
                    unique_files.append(file)
            item['file_info'] = unique_files
        
        return render_template('detail.html', item=item)
        
    except Exception as e:
        return render_template('error.html', message=f"데이터 조회 실패: {e}")


@app.route('/api/index', methods=['POST'])
def api_index():
    """데이터 정규화 및 인덱싱 API"""
    try:
        from normalize.kamco_normalizer import normalize
        from rag.embed import embed, setup_collection
        from qdrant_client import QdrantClient
        
        QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
        QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
        
        result = {'normalized': 0, 'embedded': 0, 'errors': []}
        
        try:
            result['normalized'] = normalize()
        except Exception as e:
            result['errors'].append(f'정규화 실패: {str(e)}')
            return jsonify({'success': False, 'message': '정규화 실패', 'result': result}), 500
        
        try:
            qclient = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
            cols = qclient.get_collections()
            exists = any(c.name == os.getenv("QDRANT_COLLECTION", "kamco") for c in cols.collections)
            if not exists:
                setup_collection()
        except Exception as e:
             # Just log, embed() will fail if critical
             result['errors'].append(f"Qdrant Check Failed: {e}")

        try:
            result['embedded'] = embed()
        except Exception as e:
             result['errors'].append(f'임베딩 실패: {str(e)}')
             return jsonify({'success': False, 'message': '임베딩 실패', 'result': result}), 500
             
        return jsonify({'success': True, 'message': '작업 완료', 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {e}'}), 500


@app.route('/api/delete/<item_id>', methods=['POST'])
def api_delete(item_id):
    if collection is None:
        return jsonify({'success': False, 'message': 'DB Disconnected'}), 500
    try:
        r = collection.delete_one({"_id": ObjectId(item_id)})
        if r.deleted_count > 0:
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """챗봇 API (Using Shared RAG Logic)"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'success': False, 'message': '질문을 입력하세요.'}), 400
            
        # Use smart_search which handles "recent" queries automatically
        docs = smart_search(question, limit=5)
        
        if not docs:
            # Fallback for empty
            return jsonify({
                'success': True, 
                'answer': '관련 데이터를 찾을 수 없습니다. (데이터 수집 및 임베딩이 되었는지 확인해주세요)',
                'sources': []
            })
            
        answer = generate_answer(question, docs)
        
        return jsonify({'success': True, 'answer': answer, 'sources': docs})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'}), 500


@app.template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
    if value is None: return ''
    if isinstance(value, str): return value
    return value.strftime(format)


if __name__ == '__main__':
    print("=" * 80)
    print("KAMCO Collector Web Server")
    print("=" * 80)
    
    if init_mongodb():
        print(f"✅ MongoDB Connected")
    else:
        print("⚠️  MongoDB Failed")
        
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"→ http://localhost:{port}")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=port)
