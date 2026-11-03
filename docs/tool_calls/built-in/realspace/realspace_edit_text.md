# Realspace 按字符/行列/两者同时编辑文本

注册名：`realspace_edit_text`

## 参数

path、replacement、start_char/end_char、start_line/start_column、end_line/end_column、encoding

## 返回

mode、起止字符偏移和行列、替换结果

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，且 `edit_text` 为 `true`。

文本定位全部在客户端完成：读取全文后在 `str` 上分行/切片/替换，最后整体写回。字符偏移是 0 开始，行列是 1 开始；字符按 Unicode 码点计数，不按字节。
