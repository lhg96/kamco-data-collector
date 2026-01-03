"""KAMCO MCP Server - Search and retrieve KAMCO auction data via RAG"""

import json
import logging
import os
from typing import Any, List, Dict, Optional
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Import shared logic
from rag.query import search_vector, generate_answer, smart_search

load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client.kamco
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    db = None

# Create MCP server
server = Server("kamco-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for KAMCO data operations"""
    return [
        Tool(
            name="search_kamco",
            description="Search KAMCO auction data. Supports both keyword/semantic search and 'latest/recent' queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g. 'recent apartments in Seoul')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_kamco_by_id",
            description="Get detailed information about a specific KAMCO auction item by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "The unique identifier of the auction item"
                    }
                },
                "required": ["item_id"]
            }
        ),
        Tool(
            name="get_recent_kamco",
            description="Get the most recently collected KAMCO auction listings (explicit).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="ask_kamco",
            description="Ask a question about KAMCO auctions. Returns an AI-generated answer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question about KAMCO auctions"
                    },
                    "context_limit": {
                        "type": "integer",
                        "description": "Number of context documents (default: 5)",
                        "default": 5
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="collect_kamco_data",
            description="Trigger KAMCO data collection from the API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pages": {
                        "type": "integer",
                        "description": "Number of pages to collect (default: 1)",
                        "default": 1
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="embed_kamco_data",
            description="Process and embed collected data.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

# Helper functions for direct DB access (not RAG)
def get_item_by_id(item_id: str) -> Optional[Dict]:
    """Get item from MongoDB by ID"""
    if db is None:
        return None
    try:
        from bson.objectid import ObjectId
        oid = ObjectId(item_id)
        
        # Try from collected_items first
        item = db.collected_items.find_one({"_id": oid})
        if not item:
            item = db.raw_items.find_one({"_id": oid})
            
        if item:
            item["id"] = str(item.pop("_id"))
            for k, v in item.items():
                if isinstance(v, datetime):
                    item[k] = v.isoformat()
            return item
        return None
    except Exception as e:
        logger.error(f"Get item by ID error: {e}")
        return None

def get_recent_items(limit: int = 10) -> List[Dict]:
    """Get recently collected items"""
    if db is None:
        return []
    try:
        items = list(db.collected_items.find().sort("collected_at", -1).limit(limit))
        for item in items:
            item["id"] = str(item.pop("_id"))
            if "collected_at" in item and isinstance(item["collected_at"], datetime):
                item["collected_at"] = item["collected_at"].isoformat()
        return items
    except Exception as e:
        logger.error(f"Get recent items error: {e}")
        return []

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "search_kamco":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)
        
        # Use smart_search
        results = smart_search(query, limit)
        if not results:
            return [TextContent(type="text", text="검색 결과가 없습니다.")]
        
        output = f"'{query}' 검색 결과 ({len(results)}건):\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. [유사도: {result['score']:.3f}]\n{result['text']}\n\n"
        return [TextContent(type="text", text=output)]
    
    elif name == "get_kamco_by_id":
        item_id = arguments.get("item_id", "")
        item = get_item_by_id(item_id)
        if not item:
            return [TextContent(type="text", text=f"ID '{item_id}'를 찾을 수 없습니다.")]
        return [TextContent(type="text", text=json.dumps(item, ensure_ascii=False, indent=2))]
    
    elif name == "get_recent_kamco":
        limit = arguments.get("limit", 10)
        items = get_recent_items(limit)
        if not items:
            return [TextContent(type="text", text="최근 데이터가 없습니다.")]
        output = f"최근 항목 ({len(items)}건):\n\n"
        for i, item in enumerate(items, 1):
            basic = item.get("basic_info", {})
            name = basic.get('pblancNm') or basic.get('PLNM_NM') or 'N/A'
            loc = basic.get('lctnAddr') or basic.get('LCTN_ADDR') or 'N/A'
            price = basic.get('lwsbidPrc') or basic.get('LWSBID_PRC') or 'N/A'
            output += f"{i}. {name}\n   위치: {loc}\n   가격: {price}\n\n"
        return [TextContent(type="text", text=output)]
    
    elif name == "ask_kamco":
        question = arguments.get("question", "")
        context_limit = arguments.get("context_limit", 5)
        # Use smart_search for RAG context
        docs = smart_search(question, context_limit)
        answer = generate_answer(question, docs)
        return [TextContent(type="text", text=answer)]
    
    elif name == "collect_kamco_data":
        pages = arguments.get("pages", 1)
        try:
            from services.kamco_collector_service import KamcoCollectorService
            collector = KamcoCollectorService()
            stats_summary = {"total_saved": 0}
            for p in range(1, pages + 1):
                 r = collector.run(page_no=p, num_of_rows=10, save_to_db=True)
                 stats_summary["total_saved"] += r.get("saved_items", 0)
            return [TextContent(type="text", text=f"수집 완료. 저장된 항목: {stats_summary['total_saved']}건")]
        except Exception as e:
            return [TextContent(type="text", text=f"수집 오류: {e}")]
    
    elif name == "embed_kamco_data":
        try:
            from normalize.kamco_normalizer import normalize
            from rag.embed import embed
            n = normalize()
            e = embed()
            return [TextContent(type="text", text=f"처리 완료. 정규화: {n}, 임베딩 완료.")]
        except Exception as e:
            return [TextContent(type="text", text=f"처리 오류: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
