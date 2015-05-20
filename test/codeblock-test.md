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

if __name__ = '__main__':
    print(is_markdown_file(sys.argv[1]))
```

Pylint指令：
``` bash

pylint --const-rgx='[a-z_][a-z0-9_]{2,30}$'  simplecase.py

```
以上指令可设定Pylint在检查代码时匹配常数的正则表达式


```
def f(x):
    return x ** 2
```
```
f = lambda x : x ** 2
```

Python语言中
类的声明：
``` python
class A:

    def __init__(self):
        pass

    def do_something(self):
        pass
```
类的声明使用`class`关键字
类的特殊方法`__init__`



```

double func(double (&a)[10])
{
    double average = 0;
    for(int i = 0; i < 10; i++){
        average += a[i] / 10;
    }
    return average
}

```