代码示例如下

``` python
import os, sys

def is_markdown_file(filename):
    """
    检查filename是否为已存在的Markdown文档
    """
    return os.path.isfile(filename) and (  # 检查filename是文件还是目录
             filename.lower().endswith('.md') or  # 通过后缀名检查是否属于Markdown文档
             filename.lower().endswith('.markdown') or 
             filename.lower().endswith('.mdown')
           )
```

Pylint指令：

``` bash
pylint --reports=n --disable=deprecated-module --const-rgx='[a-z_][a-z0-9_]{2,30}$'  simplecase.py
```