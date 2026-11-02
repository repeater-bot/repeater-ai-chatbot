# Realspace 按绝对字符偏移编辑文本

注册名：`realspace_edit_text_by_char`

## 参数

path、replacement、start、end、encoding

## 返回

mode=\"char\" 的编辑结果

## 白名单

需要 `writelist` 中某个条目的 `path` 覆盖目标路径，且 `edit_text_by_char` 为 `true`。

文本定位全部在客户端完成：读取全文后在 `str` 上分行/切片/替换，最后整体写回。字符偏移是 0 开始，行列是 1 开始；字符按 Unicode 码点计数，不按字节。
