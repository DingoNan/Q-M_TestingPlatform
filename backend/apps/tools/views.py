from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def tool_id_card_view(request):
    """身份证工具（常用工具 - 测试数据生成）

    前端该功能实际由 Vue 端本地生成（frontend/src/views/user/Tools.vue），
    此处保留后端入口以兼容直连访问与历史书签。

    历史缺陷：原实现 render(request, 'tool_card.html') 引用了仓库中并不存在的
    模板，导致本接口恒抛 TemplateDoesNotExist → 500。现改为返回自包含 HTML，
    不再依赖模板查找。
    """
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>身份证工具 - Q·M 测试平台</title>
<style>
  body{font-family:"Microsoft YaHei",-apple-system,sans-serif;background:#f5f7fa;
       margin:0;padding:32px;color:#1f2329}
  .card{max-width:640px;margin:0 auto;background:#fff;border-radius:12px;
        box-shadow:0 2px 12px rgba(0,0,0,.08);padding:28px 32px}
  h1{font-size:20px;margin:0 0 6px}
  p.sub{color:#8a919f;font-size:13px;margin:0 0 22px}
  label{display:block;font-size:13px;margin-bottom:6px;color:#4e5969}
  input{width:100%;box-sizing:border-box;padding:9px 12px;border:1px solid #dcdfe6;
        border-radius:6px;font-size:14px;margin-bottom:16px}
  button{background:#1a5fb4;color:#fff;border:0;border-radius:6px;padding:10px 20px;
         font-size:14px;cursor:pointer}
  button:hover{background:#154c92}
  .res{margin-top:20px;padding:14px 16px;background:#f0f6ff;border-radius:8px;
       font-family:Consolas,monospace;font-size:14px;word-break:break-all;display:none}
  .row{font-size:13px;color:#4e5969;margin-top:6px}
  .err{color:#d93026}
</style>
</head>
<body>
<div class="card">
  <h1>身份证工具</h1>
  <p class="sub">生成/校验 18 位居民身份证号（测试数据用）</p>
  <label for="region">地区码（默认 110101 北京东城）</label>
  <input id="region" value="110101" maxlength="6">
  <label for="birth">出生日期（YYYYMMDD，留空随机）</label>
  <input id="birth" placeholder="例如 19900307" maxlength="8">
  <button onclick="gen()">生成身份证号</button>
  <div class="res" id="res"></div>
  <div class="row" id="meta"></div>
</div>
<script>
var W = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2];
var C = ['1','0','X','9','8','7','6','5','4','3','2'];
function gen(){
  var region = (document.getElementById('region').value || '110101').trim();
  var birth  = (document.getElementById('birth').value || '').trim();
  if(!/^\\d{6}$/.test(region)){ show('地区码必须为 6 位数字', '', true); return; }
  if(!birth){
    var y = 1960 + Math.floor(Math.random()*45);
    var m = 1 + Math.floor(Math.random()*12);
    var d = 1 + Math.floor(Math.random()*28);
    birth = '' + y + ('0'+m).slice(-2) + ('0'+d).slice(-2);
  }
  if(!/^\\d{8}$/.test(birth)){ show('出生日期必须为 8 位数字', '', true); return; }
  var seq = ('000' + Math.floor(Math.random()*1000)).slice(-3);
  var body = region + birth + seq;
  var sum = 0;
  for(var i=0;i<17;i++){ sum += parseInt(body.charAt(i),10) * W[i]; }
  var code = body + C[sum % 11];
  show(code, '地区: ' + region + '　出生: ' + birth + '　顺序码: ' + seq);
}
function show(text, meta, isErr){
  var r = document.getElementById('res'), m = document.getElementById('meta');
  r.style.display = 'block';
  r.textContent = text;
  r.className = 'res' + (isErr ? ' err' : '');
  m.textContent = meta || '';
}
</script>
</body>
</html>"""
    return HttpResponse(html, content_type='text/html; charset=utf-8')
