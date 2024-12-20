import re
from parser import VideoSource, parse_video_id, parse_video_share_url

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI()


templates = Jinja2Templates(directory="templates")

# 创建 limiter 实例，使用 `get_remote_address` 获取客户端 IP 地址
limiter = Limiter(key_func=get_remote_address)

domlist = ['https://aweme.snssdk.com', 'https://v.douyin.com',
           'https://v11-cold.douyinvod.com', 'https://v11-cold1.douyinvod.com',
           'https://v11-coldf.douyinvod.com', 'https://v11-wha.douyinvod.com',
           'https://v18-daily-coldb.douyinvod.com', 'https://v26-cold.douyinvod.com',
           'https://v26-daily-colde.douyinvod.com', 'https://v26.douyinvod.com',
           'https://v3-b.douyinvod.com', 'https://v3-c.douyinvod.com',
           'https://v3-cold.douyinvod.com', 'https://v3-cold1.douyinvod.com',
           'https://v3-cold2.douyinvod.com', 'https://v3-cold4.douyinvod.com',
           'https://v5-coldm.douyinvod.com', 'https://v5-coldn.douyinvod.com',
           'https://v5-coldo.douyinvod.com', 'https://v5-coldr.douyinvod.com',
           'https://v5-coldu.douyinvod.com', 'https://v5-coldy.douyinvod.com',
           'https://v5-g.douyinvod.com', 'https://v5-h.douyinvod.com',
           'https://v5-wha.douyinvod.com', 'https://v9-cold.douyinvod.com',
           'https://v9-cold2.douyinvod.com', 'https://v9-wha.douyinvod.com',
           'https://v95-bj-cold.douyinvod.com', 'https://v95-hzyy-daily-colda.douyinvod.com',
           'https://v95-p-cold.douyinvod.com',
           'https://v95-zj-coldb.douyinvod.com']

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "github.com/wujunwei928/parse-video-py Demo",
        },
    )

def checkinList(url):
    with open("domain_list.txt","r") as f:
        return url in f.read()

@app.post("/get_video_url")
@limiter.limit("2/minute")  # 限制每分钟最多访问 2 次
async def share_url_parse(request: Request):
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    last_link_reg = re.compile(r"http[s]?:\/\/[^\/]+\.com")
    body = await request.json()
    shared_url = body.get("shared_url")
    video_share_url = url_reg.search(shared_url).group()
    try:
        video_info = await parse_video_share_url(video_share_url)
        if video_info.__dict__["video_url"] != "":
            last_link = video_info.__dict__["video_url"]
            last_link_prefix = last_link_reg.search(last_link).group()
            if last_link_prefix not in domlist:
                if not checkinList(last_link_prefix):
                    with open("domain_list.txt","a+") as f:
                        f.write(last_link_prefix)
                        f.write("\n")
        if len(video_info.__dict__["images"]) >0:
            for each_link in video_info.__dict__["images"]:
                last_link_prefix = last_link_reg.search(each_link).group()
                if last_link_prefix not in domlist:
                    if not checkinList(last_link_prefix):
                        with open("domain_list.txt","a+") as f:
                            f.write(last_link_prefix)
                            f.write("\n")
                
        
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/id/parse")
@limiter.limit("2/minute")  # 限制每分钟最多访问 2 次
async def video_id_parse(request: Request,source: VideoSource, video_id: str):
    try:
        video_info = await parse_video_id(source, video_id)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
