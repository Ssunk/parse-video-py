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



@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "github.com/wujunwei928/parse-video-py Demo",
        },
    )

@app.post("/get_video_url")
@limiter.limit("2/minute")  # 限制每分钟最多访问 2 次
async def share_url_parse(request: Request):
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    form_data = await request.form()
    shared_url = form_data.get('shared_url')
    video_share_url = url_reg.search(shared_url).group()
    try:
        video_info = await parse_video_share_url(video_share_url)
        print(video_info.__dict__)
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
