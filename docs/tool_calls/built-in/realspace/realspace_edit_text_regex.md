# Realspace 正则扫描并替换文本

注册名：`realspace_edit_text_regex`

## 参数

path、pattern、replacement、count、ignore_case、multiline、dotall、encoding

## 返回

替换数量、匹配位置；无匹配报错

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，且 `edit_text_regex` 为 `true`。

文本定位全部在客户端完成：读取全文后在 `str` 上分行/切片/替换，最后整体写回。字符偏移是 0 开始，行列是 1 开始；字符按 Unicode 码点计数，不按字节。
