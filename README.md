# Flask API 接口文档

## 概述
基于 Flask 框架的采集系统 API 服务，提供会员查询、订单查询和公司流水查询功能。



## Centos7环境下安装部署步骤：

##### 1.python版本要求：

Python 3.9.25

##### 2.安装命令

进入项目目录后运行以下命令安装依赖库

```
cd gzcjqctSpider
pip install -r requirements.txt
```

##### 3.开机启动服务文件：flask-gpf.service

修改文件内容如下：

WorkingDirectory=【修改为项目所在目录】

SECRET_KEY=【验证密钥】

ExecStart=【gunicorn文件路径】 --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app

日志输出路径：/var/log/spider.log

flask-gpf.service

```
[Unit]
Description=Gunicorn for flask-gpf
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/www/home/gzcjqctSpider
Environment="SECRET_KEY=XXX" "LOGIN_ACCOUNT=yyy" "PASSWORD=zzz"
ExecStart=/root/anaconda3/envs/gpfspider/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app
Restart=on-failure
RestartSec=10

# 日志重定向（备用）
StandardOutput=append:/var/log/spider.log
StandardError=append:/var/log/spider.log

[Install]
WantedBy=multi-user.target
```

##### 4.设置开机自启动

移动flask-gpf.service文件到 /etc/systemd/system/ 目录下

```
mv flask-gpf.service /etc/systemd/system/
```

##### 5.运行以下命令启动项目，并设置开机自启动

```
sudo systemctl daemon-reload
sudo systemctl enable flask-gpf
sudo systemctl start flask-gpf
```

##### 6.查看运行状态命令

```
sudo systemctl status flask-gpf
```

##### 7.重启项目服务命令

```
sudo systemctl restart flask-gpf
```

##### 



## 基础信息

- **服务地址**：根据部署环境而定
- **端口**：5000
- **认证方式**：Bearer Token 认证

## 认证机制

### Authorization 请求头
所有接口都需要在请求头中添加认证信息：

```http
Authorization: Bearer <your_token>
```

### 有效 Token
- `SECRET_KEY`：从环境变量读取
- `user_token`：测试用途

## 接口列表

---

### 1. 会员信息查询
查询会员信息及交易记录。

**接口地址**：`POST /query/member`

#### 请求头
| 参数          | 类型   | 必填 | 说明              |
| ------------- | ------ | ---- | ----------------- |
| Authorization | string | 是   | Bearer Token 认证 |

#### 请求体（JSON）
| 参数            | 类型    | 必填 | 默认值 | 说明                    |
| --------------- | ------- | ---- | ------ | ----------------------- |
| page            | integer | 否   | 0      | 页码（从0开始）         |
| size            | integer | 否   | 15     | 每页条数                |
| cellphone       | string  | 否   | -      | 手机号查询              |
| createTimeStart | integer | 否   | -      | 创建开始时间戳          |
| createTimeEnd   | integer | 否   | -      | 创建结束时间戳          |
| direction       | string  | 否   | DESC   | 排序方向：DESC 或 -DESC |

#### 请求示例
```json
{
  "page": 0,
  "size": 15,
  "cellphone": "13800138000",
  "createTimeStart": 1701360000000,
  "createTimeEnd": 1701446400000,
  "direction": "DESC"
}
```

#### 响应参数
| 参数    | 类型   | 说明         |
| ------- | ------ | ------------ |
| msg     | string | 返回信息     |
| content | array  | 查询结果列表 |

#### 响应示例
```json
{
  "msg": "success",
  "content": [
    {
      // 会员信息字段
    }
  ]
}
```

#### 错误码
| 状态码 | 错误信息                                | 说明                 |
| ------ | --------------------------------------- | -------------------- |
| 400    | page或size 参数不合法                   | 参数类型错误         |
| 400    | createTimeStart 参数不合法              | 时间戳格式错误       |
| 400    | createTimeEnd 参数不合法                | 时间戳格式错误       |
| 400    | DESC 参数不合法                         | direction 参数值错误 |
| 401    | Missing or invalid Authorization header | 缺少或无效的认证头   |
| 403    | Invalid token                           | Token 无效           |

---

### 2. 订单信息查询
查询店铺订单信息。

**接口地址**：`POST /query/order`

#### 请求头
| 参数          | 类型   | 必填 | 说明              |
| ------------- | ------ | ---- | ----------------- |
| Authorization | string | 是   | Bearer Token 认证 |

#### 请求体（JSON）
| 参数              | 类型    | 必填 | 默认值 | 说明                |
| ----------------- | ------- | ---- | ------ | ------------------- |
| page              | integer | 否   | 0      | 页码                |
| size              | integer | 否   | 15     | 每页条数            |
| orderCode         | string  | 否   | -      | 订单编号            |
| firmCode          | string  | 否   | -      | 用户编码            |
| irreversiblePhone | string  | 否   | -      | 账户                |
| payTimeStart      | integer | 否   | -      | 支付开始时间戳      |
| payTimeEnd        | integer | 否   | -      | 支付结束时间戳      |
| deliveryTimeStart | integer | 否   | -      | 发货开始时间戳      |
| deliveryTimeEnd   | integer | 否   | -      | 发货结束时间戳      |
| direction         | string  | 否   | DESC   | 排序方向            |
| orderStatus       | integer | 否   | -      | 订单状态：0,1,2,3,9 |

#### 请求示例
```json
{
  "page": 0,
  "size": 15,
  "orderCode": "ORD202500001",
  "payTimeStart": 1701360000000,
  "payTimeEnd": 1701446400000,
  "orderStatus": 1,
  "direction": "DESC"
}
```

#### 响应参数
| 参数    | 类型   | 说明     |
| ------- | ------ | -------- |
| msg     | string | 返回信息 |
| content | array  | 订单列表 |

#### 响应示例
```json
{
  "msg": "success",
  "content": [
    {
      // 订单信息字段
    }
  ]
}
```

#### 错误码
| 状态码 | 错误信息                                | 说明                 |
| ------ | --------------------------------------- | -------------------- |
| 400    | page或size 参数不合法                   | 参数类型错误         |
| 400    | payTimeStart 参数不合法                 | 时间戳格式错误       |
| 400    | payTimeEnd 参数不合法                   | 时间戳格式错误       |
| 400    | deliveryTimeStart 参数不合法            | 时间戳格式错误       |
| 400    | deliveryTimeEnd 参数不合法              | 时间戳格式错误       |
| 400    | orderStatus 参数不合法                  | 状态值不在允许范围内 |
| 400    | DESC 参数不合法                         | direction 参数值错误 |
| 401    | Missing or invalid Authorization header | 认证错误             |
| 403    | Invalid token                           | Token 无效           |

---

### 3. 公司流水查询
查询公司资金流水记录。

**接口地址**：`POST /query/firm/flow`

#### 请求头
| 参数          | 类型   | 必填 | 说明              |
| ------------- | ------ | ---- | ----------------- |
| Authorization | string | 是   | Bearer Token 认证 |

#### 请求体（JSON）
| 参数 | 类型    | 必填 | 默认值 | 说明     |
| ---- | ------- | ---- | ------ | -------- |
| page | integer | 否   | 0      | 页码     |
| size | integer | 否   | 15     | 每页条数 |

#### 请求示例
```json
{
  "page": 0,
  "size": 15
}
```

#### 响应参数
| 参数    | 类型   | 说明         |
| ------- | ------ | ------------ |
| msg     | string | 返回信息     |
| content | array  | 流水记录列表 |

#### 响应示例
```json
{
  "msg": "success",
  "content": [
    {
      // 流水记录字段
    }
  ]
}
```

#### 错误码
| 状态码 | 错误信息                                | 说明         |
| ------ | --------------------------------------- | ------------ |
| 400    | page或size 参数不合法                   | 参数类型错误 |
| 401    | Missing or invalid Authorization header | 认证错误     |
| 403    | Invalid token                           | Token 无效   |

---

## 注意事项

### 1. 日志记录
- 所有请求都会记录 IP 地址和请求头信息
- 请求和响应数据会记录到日志文件
- 日志文件：`log.log`

### 2. 环境变量
必须设置环境变量：
```bash
SECRET_KEY=your_secret_key_here
```

### 3. 时间戳格式
- 所有时间参数均使用毫秒级时间戳

### 4. 部署信息
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```
- 生产环境建议关闭 `debug=True`
- 建议使用 WSGI 服务器部署（如 Gunicorn）

### 5. 依赖包
- Flask
- loguru
- gzcjs_spider（自定义模块）

---

## 使用示例

### Python 请求示例
```python
import requests
import json

BASE_URL = "http://localhost:5000"
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 查询会员
data = {
    "page": 0,
    "size": 15,
    "cellphone": "13800138000"
}

response = requests.post(
    f"{BASE_URL}/query/member",
    headers=headers,
    json=data
)

print(response.json())
```

---



## 错误处理建议

1. 确保环境变量 `SECRET_KEY` 已正确设置
2. 检查 Token 是否在 `VALID_TOKENS` 中
3. 确保请求参数格式正确（特别是时间戳）
4. 查看日志文件 `log.log` 获取详细错误信息

---

*文档生成时间：2025-12-14
*最后更新：基于 app.py 代码分析生成*

---

将此文档保存为 `API_Documentation.md` 文件即可使用。



###### WX: shuaibin99,请我喝咖啡 (*￣︶￣)

<img src="images/wechat-qrcode.jpg" alt="1766031980889" style="zoom: 100%;" />