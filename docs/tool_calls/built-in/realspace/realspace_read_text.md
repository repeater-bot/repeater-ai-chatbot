# Realspace 读取真实文本文件

注册名：`realspace_read_text`

## 参数

path、encoding

## 返回

客户端分行、行号、字符偏移和元数据

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，且 `read_text` 为 `true`。

文本定位全部在客户端完成：读取全文后在 `str` 上分行/切片/替换，最后整体写回。字符偏移是 0 开始，行列是 1 开始；字符按 Unicode 码点计数，不按字节。
