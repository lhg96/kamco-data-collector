# kamco_gradio_collector/app.py
# Gradio-based Onbid(KAMCO) OpenAPI collector (REST, XML)

from __future__ import annotations

import os
import time
import json
import traceback
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests
import pandas as pd
import gradio as gr
import xmltodict


DEFAULT_BASE_URL = "https://openapi.onbid.co.kr/openapi/services"


def _as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _deep_get(d: Any, path: List[str], default=None):
    cur = d
    for p in path:
        if cur is None:
            return default
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return default
    return cur if cur is not None else default


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items: Dict[str, Any] = {}
    for k, v in (d or {}).items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = json.dumps(v, ensure_ascii=False)
        else:
            items[new_key] = v
    return items


def parse_onbid_xml_to_df(xml_text: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    obj = xmltodict.parse(xml_text)
    header = _deep_get(obj, ["response", "header"], {}) or {}
    body = _deep_get(obj, ["response", "body"], {}) or {}

    items = _deep_get(body, ["items"], None)

    rows: List[Dict[str, Any]] = []
    if isinstance(items, dict) and "item" in items:
        for it in _as_list(items.get("item")):
            rows.append(flatten_dict(it) if isinstance(it, dict) else {"value": it})
    elif isinstance(items, list):
        for it in items:
            rows.append(flatten_dict(it) if isinstance(it, dict) else {"value": it})
    elif isinstance(body, dict) and "item" in body:
        for it in _as_list(body.get("item")):
            rows.append(flatten_dict(it) if isinstance(it, dict) else {"value": it})

    df = pd.DataFrame(rows)
    meta = {
        "resultCode": header.get("resultCode"),
        "resultMsg": header.get("resultMsg"),
        "pageNo": body.get("pageNo"),
        "numOfRows": body.get("numOfRows"),
        "totalCount": body.get("totalCount") or body.get("TotalCount"),
    }
    return df, meta


@dataclass
class CallResult:
    url: str
    status_code: int
    elapsed_sec: float
    xml: str
    meta: Dict[str, Any]
    df: pd.DataFrame
    error: Optional[str] = None


def call_onbid(
    base_url: str,
    svc_path: str,
    operation: str,
    params: Dict[str, Any],
    timeout_sec: int = 30,
    throttle_ms: int = 250,
    user_agent: str = "Mozilla/5.0 (compatible; AIONLabs Onbid Collector/1.0; +https://aionlabs.top)",
) -> CallResult:
    base_url = base_url.rstrip("/")
    svc_path = svc_path.strip("/")
    url = f"{base_url}/{svc_path}/{operation}"

    if throttle_ms > 0:
        time.sleep(throttle_ms / 1000.0)

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/xml, text/xml;q=0.9, */*;q=0.8",
    }

    t0 = time.time()
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout_sec)
        elapsed = time.time() - t0
        xml = r.text

        try:
            df, meta = parse_onbid_xml_to_df(xml)
        except Exception:
            df, meta = pd.DataFrame(), {"parseError": "XML parse failed"}

        return CallResult(
            url=r.url,
            status_code=r.status_code,
            elapsed_sec=elapsed,
            xml=xml,
            meta=meta,
            df=df,
            error=None if r.ok else f"HTTP {r.status_code}",
        )
    except Exception as e:
        elapsed = time.time() - t0
        return CallResult(
            url=url,
            status_code=-1,
            elapsed_sec=elapsed,
            xml="",
            meta={},
            df=pd.DataFrame(),
            error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
        )


SERVICE_CATALOG = {
    "KamcoAuction": {
        "label": "캠코공매물건조회서비스",
        "svc_path": "KamcoAuctionInfoInquireSvc",
        "ops": {
            "getKamcoAuctionCltrList": "캠코공매물건목록조회",
            "getKamcoAuctionAnnounceList": "캠코공매공고목록조회",
            "getKamcoAuctionAnnounceBasicInfo": "캠코공매공고 기본정보 상세조회",
            "getKamcoAuctionScheduleList": "캠코공매일정조회",
            "getKamcoAuctionAnnounceScheduleDetail": "캠코공매공고 공매일정 상세조회",
            "getKamcoAuctionAnnounceFileDetail": "캠코공매공고 첨부파일 상세조회",
        },
    },
    "ThingInfo": {
        "label": "물건정보조회서비스(ThingInfoInquireSvc)",
        "svc_path": "ThingInfoInquireSvc",
        "ops": {
            "getUnifyUsageCltr": "통합용도별물건목록조회",
            "getUnifyUsageCltrBasicInfoDetail": "통합용도별물건 기본정보 상세조회",
            "getUnifyUsageCltrEstimationInfoDetail": "통합용도별물건 감정평가서정보 상세조회",
            "getUnifyUsageCltrRentalInfoDetail": "통합용도별물건 임대차정보 상세조회",
            "getUnifyUsageCltrRegisteredInfoDetail": "통합용도별물건 권리종류정보 상세조회",
            "getUnifyUsageCltrBidDateInfoDetail": "통합용도별물건 공매일정 상세조회",
            "getUnifyUsageCltrBidHistoryInfoDetail": "통합용도별물건 입찰이력 상세조회",
            "getUnifyUsageCltrStockholderInfoDetail": "통합용도별물건 주주정보 상세조회",
            "getUnifyUsageCltrCorporatebodyInfoDetail": "통합용도별물건 법인현황정보 상세조회",
        },
    },
}

def _build_ops(service_key: str) -> List[Tuple[str, str]]:
    ops = SERVICE_CATALOG[service_key]["ops"]
    return [(f"{k} | {v}", k) for k, v in ops.items()]


def _kv_to_dict(kv_text: str) -> Dict[str, Any]:
    kv_text = (kv_text or "").strip()
    if not kv_text:
        return {}
    if kv_text.startswith("{"):
        return json.loads(kv_text)
    out: Dict[str, Any] = {}
    for line in kv_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def run_single_call(
    base_url: str,
    service: str,
    operation: str,
    service_key: str,
    num_of_rows: int,
    page_no: int,
    throttle_ms: int,
    timeout_sec: int,
    extra_params_text: str,
):
    params = _kv_to_dict(extra_params_text)
    if service_key:
        params["serviceKey"] = service_key
    if num_of_rows:
        params["numOfRows"] = int(num_of_rows)
    if page_no:
        params["pageNo"] = int(page_no)

    svc_path = SERVICE_CATALOG[service]["svc_path"]
    res = call_onbid(
        base_url=base_url,
        svc_path=svc_path,
        operation=operation,
        params=params,
        timeout_sec=timeout_sec,
        throttle_ms=throttle_ms,
    )
    meta = {
        "request_url": res.url,
        "http_status": res.status_code,
        "elapsed_sec": round(res.elapsed_sec, 3),
        **(res.meta or {}),
    }
    if res.error:
        meta["error"] = res.error
    return res.xml, meta, res.df


def run_paged_collect(
    base_url: str,
    service: str,
    operation: str,
    service_key: str,
    num_of_rows: int,
    page_from: int,
    page_to: int,
    throttle_ms: int,
    timeout_sec: int,
    extra_params_text: str,
):
    params_base = _kv_to_dict(extra_params_text)
    if service_key:
        params_base["serviceKey"] = service_key
    params_base["numOfRows"] = int(num_of_rows)

    svc_path = SERVICE_CATALOG[service]["svc_path"]
    all_df = []
    logs = []
    for p in range(int(page_from), int(page_to) + 1):
        params = dict(params_base)
        params["pageNo"] = p

        res = call_onbid(
            base_url=base_url,
            svc_path=svc_path,
            operation=operation,
            params=params,
            timeout_sec=timeout_sec,
            throttle_ms=throttle_ms,
        )
        logs.append({
            "page": p,
            "http_status": res.status_code,
            "elapsed_sec": round(res.elapsed_sec, 3),
            "resultCode": (res.meta or {}).get("resultCode"),
            "resultMsg": (res.meta or {}).get("resultMsg"),
            "url": res.url,
            "error": res.error,
            "rows": 0 if res.df is None else len(res.df),
        })
        if res.df is not None and len(res.df) > 0:
            res.df.insert(0, "_pageNo", p)
            all_df.append(res.df)

        if (res.meta or {}).get("resultCode") in ("03", "3") or (res.df is not None and len(res.df) == 0):
            break

    log_df = pd.DataFrame(logs)
    out_df = pd.concat(all_df, ignore_index=True) if all_df else pd.DataFrame()
    return log_df.to_csv(index=False), out_df


def save_df_to_csv(df: pd.DataFrame) -> str:
    out_path = os.path.abspath("kamco_export.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


with gr.Blocks(title="KAMCO(Onbid) OpenAPI Collector") as demo:
    gr.Markdown("## KAMCO(Onbid) OpenAPI Collector\n- REST(XML) 호출 → Table 변환 → CSV 다운로드")

    with gr.Row():
        base_url = gr.Textbox(label="Base URL", value=DEFAULT_BASE_URL, scale=2)
        service = gr.Dropdown(
            label="Service",
            choices=[(v["label"], k) for k, v in SERVICE_CATALOG.items()],
            value="KamcoAuction",
            scale=1,
        )

    operation = gr.Dropdown(label="Operation", choices=_build_ops("KamcoAuction"), value=list(SERVICE_CATALOG["KamcoAuction"]["ops"].keys())[0])

    def _refresh_ops(svc_key: str):
        return gr.Dropdown.update(choices=_build_ops(svc_key), value=list(SERVICE_CATALOG[svc_key]["ops"].keys())[0])

    service.change(fn=_refresh_ops, inputs=[service], outputs=[operation])

    with gr.Row():
        service_key = gr.Textbox(label="serviceKey (URL-Encoded)", type="password", placeholder="공공데이터포털에서 발급받은 URL-Encode 키")
        timeout_sec = gr.Slider(label="Timeout (sec)", minimum=5, maximum=60, value=30, step=1)
        throttle_ms = gr.Slider(label="Throttle (ms)", minimum=0, maximum=2000, value=300, step=50)

    with gr.Row():
        num_of_rows = gr.Slider(label="numOfRows", minimum=1, maximum=1000, value=50, step=1)
        page_no = gr.Slider(label="pageNo", minimum=1, maximum=9999, value=1, step=1)

    extra_params = gr.Textbox(
        label="Extra Params (JSON or key=value lines)",
        value='{\n  "DPSL_MTD_CD": "0001",\n  "SIDO": "대전광역시"\n}',
        lines=8,
    )

    with gr.Row():
        btn_call = gr.Button("Run Single Call", variant="primary")
        btn_collect = gr.Button("Run Paged Collect")
        page_from = gr.Number(label="Page From", value=1, precision=0)
        page_to = gr.Number(label="Page To", value=5, precision=0)

    with gr.Row():
        meta_json = gr.JSON(label="Meta")
        raw_xml = gr.Code(label="Raw XML", language="html")

    df_view = gr.Dataframe(label="Result Table", interactive=False)

    with gr.Row():
        export_btn = gr.Button("Export CSV")
        export_file = gr.File(label="CSV File")

    collect_log = gr.Code(label="Collect Log (CSV)")

    btn_call.click(
        fn=run_single_call,
        inputs=[base_url, service, operation, service_key, num_of_rows, page_no, throttle_ms, timeout_sec, extra_params],
        outputs=[raw_xml, meta_json, df_view],
    )

    btn_collect.click(
        fn=run_paged_collect,
        inputs=[base_url, service, operation, service_key, num_of_rows, page_from, page_to, throttle_ms, timeout_sec, extra_params],
        outputs=[collect_log, df_view],
    )

    export_btn.click(fn=save_df_to_csv, inputs=[df_view], outputs=[export_file])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")), share=False)
