# MarkPy
a (toy) parser of Markdown implemented in pure Python

使用纯Python语言实现的简易Markdown解析器，可将Markdown文件转换为HTML页面

## 文件构成

+ `md2html.py`：主程序
+ `Parser.py`：解析器
+ `Rule.py`：解析规则

## 使用方法

``` python
python md2html.py test.md  # 将指定的输入文件test.md转换为test.html
python md2html.py input # 批量转换/input目录下的Markdown文件，结果保存到/output目录
```

程序可自动判断命令行参数`sys.argv[1]`所指的是文件还是目录

## 实现功能

标准Markdown语法：[Markdown: Syntax](http://daringfireball.net/projects/markdown/syntax)、[Markdown 语法说明](http://wowubuntu.com/markdown/index.html)

本程序目前只实现了部分语法，具体如下所示：

### 特殊字符自动转换

自动转换HTML特殊字符：`>`、`<`和`&`

Markdown输入：

``` Markdown
<  >  &
```

HTML输出：

``` html
&lt;  &gt;  &amp;
```

### 段落

Markdown输入：
``` Markdown
道可道，非常道。
名可名，非常名。

无名天地之始。

有名万物之母。
```

HTML输出：
``` html
<p>道可道，非常道。
名可名，非常名。</p>
<p>无名天地之始。</p>
<p>有名万物之母。</p>
```


### 标题

##### Setext风格

Markdown输入：

``` Markdown
一级标题
=============

二级标题
-------------
```

HTML输出：

``` html
<h1>一级标题</h1>

<h2>二级标题</h2>
```

##### Atx风格

Markdown输入：

``` Markdown
# 一级标题

## 二级标题

### 三级标题

#### 四级标题

##### 五级标题

###### 六级标题
```

HTML输出：

``` html
<h1>一级标题</h1>

<h2>二级标题</h2>

<h3>三级标题</h3>

<h4>四级标题</h4>

<h5>五级标题</h5>

<h6>六级标题</h6>
```

**[TODO]**：暂不支持如下“闭合”形式Atx风格标题（close Atx-style headers）：

``` Markdown
# 一级标题 #

## 二级标题 ##

### 三级标题  #######
```

### 区块引用

Markdown输入：

``` Markdown
> 轻轻的我走了

> 正如我轻轻的来

> 我轻轻的招手

> 作别西天的云彩
```

HTML输出：

``` html
<blockquote>
 轻轻的我走了</p>
<p> 正如我轻轻的来</p>
<p> 我轻轻的招手</p>
<p> 作别西天的云彩</p>
</blockquote>
```

### 列表

Markdown输入：

``` Markdown
无序列表：

+ 甲
+ 乙
+ 丙

无序列表：

- 甲
- 乙
- 丙

无序列表：

* 甲
* 乙
* 丙

有序列表：

1. 甲
2. 乙
3. 丙
```

HTML输出：

``` html
<p></ol>
无序列表：</p>
<p><ul>
<li>甲</li>

<li>乙</li>

<li>丙</li>
</p>
<p></ul>
无序列表：</p>
<p><ul>
<li>甲</li>

<li>乙</li>

<li>丙</li>
</p>
<p></ul>
无序列表：</p>
<p><ul>
<li>甲</li>

<li>乙</li>

<li>丙</li>
</p>
<p></ul>
有序列表：</p>
<p><ol>
<li>甲</li>

<li>乙</li>

<li>丙</li>
</p>
```