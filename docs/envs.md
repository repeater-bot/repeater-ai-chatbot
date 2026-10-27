# 环境变量表

用于引导主配置
添加 API_Key
以及设置一些服务器启动配置

| 环境变量 | 描述 | 是否必填 | 默认值(*示例值*) |
| :---: | :---: | :---: | :---: |
| `ADMIN_API_KEY` | 管理员API_Key (用于Repeater的管理员操作身份验证) | **选填但生产环境建议填写</br>如果填写的不够随机，程序会报错</br>建议先执行一次取生成的API_Key** | *\*自动生成随机 API Key* |
| `CONFIG_DIR` | 配置文件夹路径 | **选填** | `./config/project_config` |
| `CONFIG_FORCE_LOAD_LIST` | 配置文件强制加载列表(元素为配置文件路径) | **选填** | *`["./config/project_config/configs.json", "./config/project_config/configs2.json"]`* |
| `METASO_API_KEY` | Metaso API_Key (用于Metaso的API调用) | **选填，但如果使用 Metaso 工具则必填** | |
| `DEEPSEEK_API_KEY` | Deepseek API_Key (用于Deepseek的API调用) | **选填，但如果使用 Deepseek 工具则必填** | |
| `HOST` | 服务监听的IP | **选填** | `0.0.0.0` |
| `PORT` | 服务监听的端口 | **选填** | `8080` |
| `WORKERS` | 服务监听的进程数 | **选填** | `1` |
| `RELOAD` | 是否自动重启 | **选填** | `false` |