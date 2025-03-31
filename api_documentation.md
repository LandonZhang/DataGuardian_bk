# Data Guardian API 文档

---



# 规则管理 API 文档

## 规则上传模块

### 下载规则模板

获取规则导入的Excel模板文件。

**请求URL**：`http://127.0.0.1:8080/rule/upload/`

**请求方式**：`GET`

**响应格式**：`Excel文件`

**响应说明**：

- 成功：返回Excel模板文件
- 失败：返回404状态码及错误信息

### 上传规则文件

上传Excel规则文件并保存到数据库。

**请求URL**：`http://127.0.0.1:8080/rule/upload/`

**请求方式**：`POST`

**请求参数**：

| 参数名 | 类型 | 是否必须 | 说明                 |
| ------ | ---- | -------- | -------------------- |
| file   | File | 是       | Excel文件(.xlsx格式) |

**请求格式**：`form-data`

**响应格式**：`JSON`

**响应参数**：

| 参数名        | 类型    | 说明                         |
| ------------- | ------- | ---------------------------- |
| status        | string  | 状态（成功为"success"）      |
| message       | string  | 返回消息                     |
| total_records | integer | 总记录数                     |
| success_count | integer | 成功导入数量                 |
| error_count   | integer | 错误记录数量                 |
| error_details | array   | 错误详情，包含行号和错误信息 |

**响应示例**：

```json
{
  "status": "success",
  "message": "成功导入 5 条规则",
  "total_records": 6,
  "success_count": 5,
  "error_count": 1,
  "error_details": [
    {
      "行号": 3,
      "错误": "必填字段不能为空"
    }
  ]
}
```

**错误码说明**：

- 400: 文件格式错误或缺少必要列
- 500: 服务器内部错误

## 规则查询模块

### 获取项目名称下拉选项

获取所有不重复的项目名称作为下拉选项。

**请求URL**：`http://127.0.0.1:8080/rule/search/project`

**请求方式**：`GET`

**示例URL**：

```
http://127.0.0.1:8080/rule/search/project
```

---

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型  | 说明         |
| ------- | ----- | ------------ |
| options | array | 项目名称列表 |

**响应示例**：

```json
{
  "options": ["项目A", "项目B", "项目C"]
}
```

### 获取表格名称下拉选项

获取所有不重复的表格名称作为下拉选项，可根据项目名称筛选。

**请求URL**：`http://127.0.0.1:8080/rule/search/table`

**请求方式**：`GET`

**请求参数**：

| 参数名       | 类型         | 是否必须 | 说明             |
| ------------ | ------------ | -------- | ---------------- |
| project_name | List[string] | 否       | 项目名称筛选条件 |

**响应格式**：`JSON`

**单个项目示例URL**：

```
http://127.0.0.1:8080/rule/search/table?project_name=测试项目1
```

**多个项目示例URL**：

```
http://127.0.0.1:8080/rule/search/table?project_name=测试项目1&project_name=测试项目2
```

---

**响应参数**：

| 参数名  | 类型  | 说明         |
| ------- | ----- | ------------ |
| options | array | 表格名称列表 |

**响应示例**：

```json
{
  "options": ["表格1", "表格2", "表格3"]
}
```

### 获取特征名称下拉选项

获取所有不重复的特征名称作为下拉选项，可根据项目名称和表格名称筛选。

**请求URL**：`http://127.0.0.1:8080/rule/search/feature`

**请求方式**：`GET`

**请求参数**：

| 参数名       | 类型         | 是否必须 | 说明             |
| ------------ | ------------ | -------- | ---------------- |
| project_name | List[string] | 否       | 项目名称筛选条件 |
| table_name   | List[string] | 否       | 表格名称筛选条件 |

**单个项目和表格示例URL**：

```
http://127.0.0.1:8080/rule/search/feature?project_name=测试项目1&table_name=表格A
```

**多个项目和表格示例URL**：

```
http://127.0.0.1:8080/rule/search/feature?project_name=测试项目1&project_name=测试项目2&table_name=表格A&table_name=表格B
```

---

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型  | 说明         |
| ------- | ----- | ------------ |
| options | array | 特征名称列表 |

**响应示例**：

```json
{
  "options": ["特征1", "特征2", "特征3"]
}
```

### 搜索规则数据

根据条件搜索规则数据，支持分页查询。

**请求URL**：`http://127.0.0.1:8080/rule/search/`

**请求方式**：`GET`

**请求参数**：

| 参数名       | 类型    | 是否必须 | 说明                        |
| ------------ | ------- | -------- | --------------------------- |
| project_name | string  | 否       | 项目名称筛选条件            |
| table_name   | string  | 否       | 表格名称筛选条件            |
| feature_name | string  | 否       | 特征名称筛选条件            |
| start_time   | string  | 否       | 创建开始时间 (YYYY-MM-DD)   |
| end_time     | string  | 否       | 创建结束时间 (YYYY-MM-DD)   |
| page         | integer | 否       | 页码，默认为1               |
| page_size    | integer | 否       | 每页数量，默认为10，最大100 |

**基本搜索示例URL**：

```
http://127.0.0.1:8080/rule/search/?project_name=测试项目1&table_name=表格A&page=1&page_size=20
```

**多条件组合搜索示例URL**：

```
http://127.0.0.1:8080/rule/search/?project_name=测试项目1&project_name=测试项目2&table_name=表格A&table_name=表格B&feature_name=特征X&start_time=2024-01-01&end_time=2024-03-24&page=2&page_size=15
```

---

**响应格式**：`JSON`

**响应参数**：

| 参数名 | 类型    | 说明         |
| ------ | ------- | ------------ |
| total  | integer | 总记录数     |
| data   | array   | 规则数据列表 |

**data数组中的对象结构**：

| 参数名        | 类型        | 说明     |
| ------------- | ----------- | -------- |
| id            | integer     | 规则ID   |
| project_name  | string      | 项目名称 |
| table_name    | string      | 表格名称 |
| feature_name  | string      | 特征名称 |
| rule_content  | string      | 对应规则 |
| error_type    | string      | 错误类型 |
| issue_details | string/null | 问题详情 |
| created_at    | string      | 创建时间 |

**响应示例**：

```json
{
  "total": 25,
  "data": [
    {
      "id": 1,
      "project_name": "项目A",
      "table_name": "表格1",
      "feature_name": "特征1",
      "rule_content": "规则内容",
      "error_type": "类型错误",
      "issue_details": "详细问题描述",
      "created_at": "2023-03-15T12:34:56"
    },
    {
      "id": 2,
      "project_name": "项目B",
      "table_name": "表格2",
      "feature_name": "特征2",
      "rule_content": "规则内容2",
      "error_type": "逻辑错误",
      "issue_details": null,
      "created_at": "2023-03-14T10:24:36"
    }
  ]
}
```

**错误码说明**：

- 400: 请求参数错误（如日期格式）
- 500: 服务器内部错误

### 重置搜索条件

重置所有搜索条件，返回所有规则数据（带分页）。

**请求URL**：`http://127.0.0.1:8080/rule/search/reset`

**请求方式**：`GET`

**请求参数**：

| 参数名    | 类型    | 是否必须 | 说明                        |
| --------- | ------- | -------- | --------------------------- |
| page      | integer | 否       | 页码，默认为1               |
| page_size | integer | 否       | 每页数量，默认为10，最大100 |

**示例URL**：

```
http://127.0.0.1:8080/rule/search/reset?page=1&page_size=20
```

---

**响应格式**：`JSON`

**响应参数**： 与==搜索规则数据==接口相同

**响应示例**： 与==搜索规则数据==接口相同

**错误码说明**：

- 500: 服务器内部错误

## 规则管理模块

manageRuleRouter 的访问前缀是：`http://127.0.0.1:8080/rule/manage`

### 查看单条规则数据详情

获取指定 ID 的规则数据详细信息。

**请求URL**：`http://127.0.0.1:8080/rule/manage/{rule_id}`

**请求方式**：`GET`

**路径参数**：

| 参数名  | 类型    | 是否必须 | 说明                  |
| ------- | ------- | -------- | --------------------- |
| rule_id | integer | 是       | 规则ID，必须大于等于1 |

**响应格式**：`JSON`

**响应参数**：

| 参数名        | 类型        | 说明     |
| ------------- | ----------- | -------- |
| id            | integer     | 规则ID   |
| project_name  | string      | 项目名称 |
| table_name    | string      | 表格名称 |
| feature_name  | string      | 特征名称 |
| rule_content  | string      | 对应规则 |
| error_type    | string      | 错误类型 |
| issue_details | string/null | 问题详情 |
| created_at    | string      | 创建时间 |
| updated_at    | string      | 更新时间 |

**响应示例**：

```json
{
  "id": 1,
  "project_name": "项目A",
  "table_name": "表格1",
  "feature_name": "特征1",
  "rule_content": "规则内容",
  "error_type": "类型错误",
  "issue_details": "详细问题描述",
  "created_at": "2023-03-15 12:34:56",
  "updated_at": "2023-03-16 10:45:30"
}
```

**错误码说明**：

- 404: 指定ID的规则不存在
- 500: 服务器内部错误

### 更新规则数据

更新指定 ID 的规则数据。

**请求URL**：`http://127.0.0.1:8080/rule/manage/{rule_id}`

**请求方式**：`PUT`

**路径参数**：

| 参数名  | 类型    | 是否必须 | 说明                  |
| ------- | ------- | -------- | --------------------- |
| rule_id | integer | 是       | 规则ID，必须大于等于1 |

**请求体**：

```json
{
  "project_name": "更新后的项目名称",
  "table_name": "更新后的表格名称",
  "feature_name": "更新后的特征名称",
  "rule_content": "更新后的规则内容",
  "error_type": "更新后的错误类型",
  "issue_details": "更新后的问题详情"
}
```

**请求参数说明**：

| 参数名        | 类型   | 是否必须 | 说明     |
| ------------- | ------ | -------- | -------- |
| project_name  | string | 否       | 项目名称 |
| table_name    | string | 否       | 表格名称 |
| feature_name  | string | 否       | 特征名称 |
| rule_content  | string | 否       | 对应规则 |
| error_type    | string | 否       | 错误类型 |
| issue_details | string | 否       | 问题详情 |

**注意**：所有字段均为可选，未提供的字段将保持原值不变。但至少需要提供一个字段进行更新。

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型   | 说明                      |
| ------- | ------ | ------------------------- |
| status  | string | 操作状态，成功为"success" |
| message | string | 操作结果信息              |

**响应示例**：

```json
{
  "status": "success",
  "message": "成功更新ID为1的规则数据"
}
```

**错误码说明**：

- 400: 未提供任何需要更新的字段
- 404: 指定ID的规则不存在
- 500: 服务器内部错误

### 删除规则数据

删除指定 ID 的规则数据。

**请求URL**：`http://127.0.0.1:8080/rule/manage/{rule_id}`

**请求方式**：`DELETE`

**路径参数**：

| 参数名  | 类型    | 是否必须 | 说明                  |
| ------- | ------- | -------- | --------------------- |
| rule_id | integer | 是       | 规则ID，必须大于等于1 |

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型   | 说明                      |
| ------- | ------ | ------------------------- |
| status  | string | 操作状态，成功为"success" |
| message | string | 操作结果信息              |

**响应示例**：

```json
{
  "status": "success",
  "message": "成功删除ID为1的规则数据"
}
```

**错误码说明**：

- 404: 指定ID的规则不存在
- 500: 服务器内部错误

### 批量删除规则数据

批量删除多条规则数据。

**请求URL**：`http://127.0.0.1:8080/rule/manage/batch-delete`

**请求方式**：`POST`

**请求体**：

```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**请求参数说明**：

| 参数名 | 类型  | 是否必须 | 说明               |
| ------ | ----- | -------- | ------------------ |
| ids    | array | 是       | 要删除的规则ID列表 |

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型   | 说明                      |
| ------- | ------ | ------------------------- |
| status  | string | 操作状态，成功为"success" |
| message | string | 操作结果信息              |

**响应示例**：

```json
{
  "status": "success",
  "message": "成功删除5条规则数据"
}
```

**错误码说明**：

- 400: 删除ID列表不能为空
- 500: 服务器内部错误



# 大语言模型交互 API 文档

## LLM 对话模块

llmChatRouter 的访问前缀是：`http://127.0.0.1:8080/llm/chat`

### 与大模型对话(流式响应)

使用流式响应方式与大模型进行对话，适用于实时显示回答。

**请求URL**：`http://127.0.0.1:8080/llm/chat/stream`

**请求方式**：`POST`

**请求体**：

```json
{
  "query": "请问如何优化MySQL查询性能？",
  "conversation_id": "conv_12345",
  "user": "user_67890"
}
```

**请求参数说明**：

| 参数名          | 类型   | 是否必须 | 说明                                                   |
| --------------- | ------ | -------- | ------------------------------------------------------ |
| query           | string | 是       | 用户的问题或输入                                       |
| conversation_id | string | 否       | 对话ID，不提供则使用保存的值，提供空字符串则开始新对话 |
| user            | string | 是       | 用户标识符                                             |

**响应格式**：`text/event-stream` (SSE)

**响应示例**：

```
data: {"event": "message", "answer": "要优化MySQL查询性能", "conversation_id": "conv_abc123", "id": "msg_123456"}

data: {"event": "message", "answer": "要优化MySQL查询性能，您可以：", "conversation_id": "conv_abc123", "id": "msg_123456"}

data: {"event": "message", "answer": "要优化MySQL查询性能，您可以：\n1. 建立合适的索引", "conversation_id": "conv_abc123", "id": "msg_123456"}

...

data: {"event": "message_end", "answer": "要优化MySQL查询性能，您可以：\n1. 建立合适的索引\n2. 优化查询语句\n3. 合理设计表结构\n4. 使用查询缓存\n5. 适当分表分库", "conversation_id": "conv_abc123", "id": "msg_123456"}

data: {"event": "done"}
```

**错误响应**：

```
data: {"event": "error", "message": "错误信息"}
```

### 与大模型对话(完整响应)

与大模型进行对话，返回完整的回答（非流式）。

**请求URL**：`http://127.0.0.1:8080/llm/chat`

**请求方式**：`POST`

**请求体**：

```json
{
  "query": "请问如何优化MySQL查询性能？",
  "conversation_id": "conv_12345",
  "user": "user_67890"
}
```

**请求参数说明**：

| 参数名          | 类型   | 是否必须 | 说明                                                   |
| --------------- | ------ | -------- | ------------------------------------------------------ |
| query           | string | 是       | 用户的问题或输入                                       |
| conversation_id | string | 否       | 对话ID，不提供则使用保存的值，提供空字符串则开始新对话 |
| user            | string | 是       | 用户标识符                                             |

**响应格式**：`JSON`

**响应参数**：

| 参数名          | 类型    | 说明             |
| --------------- | ------- | ---------------- |
| answer          | string  | 大模型的回答内容 |
| conversation_id | string  | 对话ID           |
| created_at      | integer | 创建时间戳       |
| id              | string  | 消息ID           |

**响应示例**：

```json
{
  "answer": "要优化MySQL查询性能，您可以：\n1. 建立合适的索引\n2. 优化查询语句\n3. 合理设计表结构\n4. 使用查询缓存\n5. 适当分表分库",
  "conversation_id": "conv_abc123",
  "created_at": 1679123456,
  "id": "msg_123456"
}
```

**错误码说明**：

- 500: 处理请求时发生错误
- 504: 与Dify通信超时

### 生成用户ID

生成一个唯一的用户ID，用于标识用户。

**请求URL**：`http://127.0.0.1:8080/llm/chat/generate-user-id`

**请求方式**：`GET`

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型   | 说明             |
| ------- | ------ | ---------------- |
| user_id | string | 生成的唯一用户ID |

**响应示例**：

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 开始新对话

为指定用户开始一个新的对话。

**请求URL**：`http://127.0.0.1:8080/llm/chat/new-conversation`

**请求方式**：`POST`

**请求体**：

```json
{
  "user": "user_67890"
}
```

**请求参数说明**：

| 参数名 | 类型   | 是否必须 | 说明       |
| ------ | ------ | -------- | ---------- |
| user   | string | 是       | 用户标识符 |

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型   | 说明         |
| ------- | ------ | ------------ |
| status  | string | 操作状态     |
| message | string | 操作结果信息 |
| user    | string | 用户标识符   |

**响应示例**：

```json
{
  "status": "success",
  "message": "已开始新对话",
  "user": "user_67890"
}
```

### 获取当前对话ID

获取指定用户当前的对话ID。

**请求URL**：`http://127.0.0.1:8080/llm/chat/conversation-id/{user}`

**请求方式**：`GET`

**路径参数**：

| 参数名 | 类型   | 是否必须 | 说明       |
| ------ | ------ | -------- | ---------- |
| user   | string | 是       | 用户标识符 |

**响应格式**：`JSON`

**响应参数**：

| 参数名          | 类型   | 说明                             |
| --------------- | ------ | -------------------------------- |
| user            | string | 用户标识符                       |
| conversation_id | string | 当前对话ID，如果没有则为空字符串 |

**响应示例**：

```json
{
  "user": "user_67890",
  "conversation_id": "conv_abc123"
}
```

# 数据库操作API文档

## 数据库连接模块

linkDatabaseRouter 的访问前缀是：`http://127.0.0.1:8080/database/link`

### 连接MySQL数据库

连接MySQL数据库并保存连接配置。

**请求URL**：`http://127.0.0.1:8080/database/link/`

**请求方式**：`POST`

**请求体**：

```json
{
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "123456",
  "database": "test_db",
  "charset": "utf8mb4"
}
```

**请求参数说明**：

| 参数名   | 类型    | 是否必须 | 说明                   |
| -------- | ------- | -------- | ---------------------- |
| host     | string  | 是       | 数据库主机地址         |
| port     | integer | 否       | 数据库端口，默认为3306 |
| user     | string  | 是       | 数据库用户名           |
| password | string  | 是       | 数据库密码             |
| database | string  | 是       | 数据库名称             |
| charset  | string  | 否       | 字符集，默认为utf8mb4  |

**响应格式**：`JSON`

**响应参数**：

| 参数名          | 类型        | 说明                      |
| --------------- | ----------- | ------------------------- |
| status          | string      | 操作状态，成功为"success" |
| message         | string      | 操作结果信息              |
| connection_info | object/null | 连接成功时返回的连接信息  |

**响应示例**：

```json
{
  "status": "success",
  "message": "成功连接到数据库",
  "connection_info": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "database": "test_db",
    "charset": "utf8mb4"
  }
}
```

**错误码说明**：

- 400: 无法连接到数据库，请检查连接参数是否正确
- 500: 处理数据库连接请求时出错

### 测试MySQL数据库连接

测试MySQL数据库连接，但不保存配置，用户可以先测试，成功后再保存。

**请求URL**：`http://127.0.0.1:8080/database/link/test`

**请求方式**：`POST`

**请求体**：

```json
{
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "123456",
  "database": "test_db",
  "charset": "utf8mb4"
}
```

**请求参数说明**：

| 参数名   | 类型    | 是否必须 | 说明                   |
| -------- | ------- | -------- | ---------------------- |
| host     | string  | 是       | 数据库主机地址         |
| port     | integer | 否       | 数据库端口，默认为3306 |
| user     | string  | 是       | 数据库用户名           |
| password | string  | 是       | 数据库密码             |
| database | string  | 是       | 数据库名称             |
| charset  | string  | 否       | 字符集，默认为utf8mb4  |

**响应格式**：`JSON`

**响应参数**：

| 参数名          | 类型        | 说明                         |
| --------------- | ----------- | ---------------------------- |
| status          | string      | 操作状态，"success"或"error" |
| message         | string      | 操作结果信息                 |
| connection_info | object/null | 连接成功时返回的连接信息     |

**响应示例（成功）**：

```json
{
  "status": "success",
  "message": "数据库连接测试成功",
  "connection_info": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "database": "test_db",
    "charset": "utf8mb4"
  }
}
```

**响应示例（失败）**：

```json
{
  "status": "error",
  "message": "数据库连接测试失败，请检查连接参数",
  "connection_info": null
}
```

### 获取已保存的数据库配置

获取已保存的数据库配置信息，便于用户下次登录时直接显示已保存信息。

**请求URL**：`http://127.0.0.1:8080/database/link/config`

**请求方式**：`GET`

**响应格式**：`JSON`

**响应参数**：

| 参数名  | 类型        | 说明                                 |
| ------- | ----------- | ------------------------------------ |
| status  | string      | 操作状态，"success"、"info"或"error" |
| message | string      | 操作结果信息                         |
| config  | object/null | 已保存的数据库配置信息               |

**响应示例（配置存在）**：

```json
{
  "status": "success",
  "message": "成功获取保存的数据库配置",
  "config": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "test_db",
    "charset": "utf8mb4"
  }
}
```

password 前端可以考虑加密成: “****”, 让用户选择是否显示。

**响应示例（配置不存在）**：

```json
{
  "status": "info",
  "message": "未找到保存的数据库配置",
  "config": null
}
```

**响应示例（出错）**：

```json
{
  "status": "error",
  "message": "获取数据库配置时出错: 详细错误信息",
  "config": null
}
```