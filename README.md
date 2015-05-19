# MarkPy
a (toy) parser of Markdown implemented in pure Python 3.x, no need for third-party modules

使用纯Python语言实现的简易Markdown解析器，可将Markdown文件转换为HTML页面

## 文件构成

+ `md2html.py`：主程序
+ `Parser.py`：解析器
+ `Rule.py`：解析规则
+ `/test`：测试样例 `python md2html test`

## 使用方法

``` python
python md2html.py test.md  # 将指定的输入文件test.md转换为test.html
python md2html.py input # 批量转换/input目录下的Markdown文件，结果保存到/output目录
```

程序可自动判断命令行参数`sys.argv[1]`所指的是文件还是目录

## 实现功能

Markdown语法参考：[Markdown: Syntax](http://daringfireball.net/projects/markdown/syntax)、[Markdown 语法说明](http://wowubuntu.com/markdown/index.html)、[GitHub Flavored Markdown](https://help.github.com/articles/github-flavored-markdown)

本程序目标是实现下列语法：

- [x] [兼容HTML标签](http://daringfireball.net/projects/markdown/syntax#html)
- [x] [特殊字符自动转换（`>`、`<`和`&`）](http://daringfireball.net/projects/markdown/syntax#autoescape)
- [x] [段落](http://daringfireball.net/projects/markdown/syntax#p)
- [x] [Setext风格标题](http://daringfireball.net/projects/markdown/syntax#header)
- [x] [Atx风格标题](http://daringfireball.net/projects/markdown/syntax#header)
- [x] [区块引用](http://daringfireball.net/projects/markdown/syntax#blockquote)
- [ ] [列表](http://daringfireball.net/projects/markdown/syntax#list)   :exclamation:**TODO**：支持列表的缩进嵌套
- [x] [行内代码](http://daringfireball.net/projects/markdown/syntax#code)
- [x] [行间代码块（GitHub flavored fenced code blocks）](https://help.github.com/articles/github-flavored-markdown/#fenced-code-blocks)
- [x] [水平分隔线](http://daringfireball.net/projects/markdown/syntax#hr)
- [x] [行间式超链接（inline-style links）](http://daringfireball.net/projects/markdown/syntax#link)
- [ ] [参考式超链接（reference-style links）](http://daringfireball.net/projects/markdown/syntax#link)   :exclamation:**TODO**：支持参考式超链接
- [x] [网址自动连接](http://daringfireball.net/projects/markdown/syntax#autolink)
- [x] [Email自动连接](http://daringfireball.net/projects/markdown/syntax#autolink)
- [x] [行间式图片链接](http://daringfireball.net/projects/markdown/syntax#img)
- [ ] [参考式图片链接](http://daringfireball.net/projects/markdown/syntax#img)    :exclamation:**TODO**：支持参考式图片链接
- [x] [强调](http://daringfireball.net/projects/markdown/syntax#em)
- [x] [反斜杠逃逸](http://daringfireball.net/projects/markdown/syntax#backslash)