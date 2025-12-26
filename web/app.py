"""
KAMCO Public Auction Data Collection Web Application

Usage:
  python web/app.py

Environment Variables (.env):
  KAMCO_API_KEY - KAMCO API service key
  MONGO_URI - MongoDB connection URI (default: mongodb://localhost:27017)
  FLASK_SECRET_KEY - Flask secret key for session management
  FLASK_PORT - Flask port (default: 5000)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.kamco_collector_service import KamcoCollectorService

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
        # 수집 방식
        collect_mode = request.form.get('collect_mode', 'list')
        
        # 수집 서비스 초기화
        service = KamcoCollectorService(
            db_name=MONGO_DB_NAME,
            collection_name=MONGO_COLLECTION_NAME
        )
        
        # MongoDB 연결
        if not service.connect_mongodb():
            return jsonify({
                'success': False,
                'message': 'MongoDB 연결 실패'
            }), 500
        
        if collect_mode == 'latest':
            # 최신 공고 수집
            days = int(request.form.get('days', 180))
            max_count = int(request.form.get('max_count', 10))
            
            stats = collect_latest_announces_internal(service, days, max_count)
        else:
            # 공고 목록 수집
            page_no = int(request.form.get('page_no', 1))
            num_of_rows = int(request.form.get('num_of_rows', 10))
            prpt_dvsn_cd = request.form.get('prpt_dvsn_cd', '0001')
            
            stats = service.run(
                page_no=page_no,
                num_of_rows=num_of_rows,
                prpt_dvsn_cd=prpt_dvsn_cd,
                save_to_db=True
            )
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f'{stats["saved_items"]}개 항목이 수집되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'수집 실패: {str(e)}'
        }), 500


def collect_latest_announces_internal(service, days, max_count):
    """최신 공고 수집 내부 함수"""
    import requests
    import xmltodict
    from datetime import timedelta
    
    # 날짜 범위
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    # 1. 일정 조회
    url = f"{service.base_url}/{service.service_path}/getKamcoPbctSchedule"
    params = {
        'serviceKey': service.service_key,
        'pageNo': 1,
        'numOfRows': max_count * 3,
        'PRPT_DVSN_CD': '0001',
        'STRT_DT': start_date.strftime('%Y%m%d'),
        'END_DT': today.strftime('%Y%m%d')
    }
    
    res = requests.get(url, params=params, headers=service.headers, timeout=service.timeout)
    res.raise_for_status()
    
    payload = xmltodict.parse(res.text)
    body = (payload.get('response') or {}).get('body') or {}
    items = body.get('items', {}).get('item', [])
    
    if not items:
        return service.stats
    
    item_list = items if isinstance(items, list) else [items]
    
    # 중복 제거
    announces = {}
    for item in item_list:
        plnm_no = item.get('PLNM_NO')
        pbct_no = item.get('PBCT_NO')
        if plnm_no and plnm_no not in announces:
            announces[plnm_no] = {'PLNM_NO': plnm_no, 'PBCT_NO': pbct_no}
    
    announce_list = list(announces.values())[:max_count]
    service.stats["total_announces"] = len(announce_list)
    
    # 2. 상세 정보 수집
    for announce in announce_list:
        try:
            data = service.collect_announce_details(announce)
            if data:
                service.save_to_mongodb(data)
                service.stats["processed_announces"] += 1
                service.stats["saved_items"] += 1
            else:
                service.stats["failed_announces"] += 1
        except Exception:
            service.stats["failed_announces"] += 1
    
    return service.stats


@app.route('/list')
def list_page():
    """수집 리스트 게시판"""
    if collection is None:
        return render_template('error.html', message="MongoDB 연결이 필요합니다.")
    
    try:
        # 페이지네이션
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 검색
        search_query = request.args.get('q', '')
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"PLNM_NO": {"$regex": search_query, "$options": "i"}},
                    {"PBCT_NO": {"$regex": search_query, "$options": "i"}},
                    {"announce_list_item.PLNM_NM": {"$regex": search_query, "$options": "i"}},
                ]
            }
        
        # 전체 개수
        total_count = collection.count_documents(query)
        
        # 데이터 조회 (공고번호, 공매번호 내림차순)
        skip = (page - 1) * per_page
        items = list(collection.find(query).sort([("PLNM_NO", DESCENDING), ("PBCT_NO", DESCENDING)]).skip(skip).limit(per_page))
        
        # 페이지 정보
        total_pages = (total_count + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None,
        }
        
        return render_template('list.html', items=items, pagination=pagination, search_query=search_query)
        
    except Exception as e:
        return render_template('error.html', message=f"데이터 조회 실패: {e}")


@app.route('/detail/<item_id>')
def detail_page(item_id):
    """상세 보기 페이지"""
    if collection is None:
        return render_template('error.html', message="MongoDB 연결이 필요합니다.")
    
    try:
        from bson.objectid import ObjectId
        item = collection.find_one({"_id": ObjectId(item_id)})
        
        if not item:
            return render_template('error.html', message="데이터를 찾을 수 없습니다.")
        
        # 첨부파일 중복 제거 (추가 보호)
        if item.get('file_info'):
            seen = set()
            unique_files = []
            for file in item['file_info']:
                file_id = file.get('ATCH_FILE_PTCS_NO')
                if file_id and file_id not in seen:
                    seen.add(file_id)
                    unique_files.append(file)
            item['file_info'] = unique_files
        
        return render_template('detail.html', item=item)
        
    except Exception as e:
        return render_template('error.html', message=f"데이터 조회 실패: {e}")


@app.route('/api/delete/<item_id>', methods=['POST'])
def api_delete(item_id):
    """데이터 삭제 API"""
    if collection is None:
        return jsonify({'success': False, 'message': 'MongoDB 연결이 필요합니다.'}), 500
    
    try:
        from bson.objectid import ObjectId
        result = collection.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': '삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '삭제할 데이터가 없습니다.'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'삭제 실패: {str(e)}'}), 500


@app.template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
    """날짜 시간 포맷 필터"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    return value.strftime(format)


if __name__ == '__main__':
    print("=" * 80)
    print("KAMCO 공매 데이터 수집 관리 시스템")
    print("=" * 80)
    
    # MongoDB 연결
    print("→ MongoDB 연결 중...")
    if init_mongodb():
        print(f"✅ MongoDB 연결 성공 ({MONGO_DB_NAME}.{MONGO_COLLECTION_NAME})")
    else:
        print("⚠️  MongoDB 연결 실패 - 일부 기능이 제한될 수 있습니다.")
    
    print()
    print("=" * 80)
    print("웹 서버 시작")
    print("=" * 80)
    
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"→ http://localhost:{port}")
    print("=" * 80)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=port)
