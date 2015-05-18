"""
将Markdown文件转换为HTML文件

使用：
    (1). python md2html.py test.md  # 将指定的输入文件test.md转换为test.html
    (2). python md2html.py input # 批量转换/input目录下的Markdown文件，结果保存到/output目录
"""

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



if __name__ == '__main__':  # 主程序

    from Parser import Parser

    input_files = []  # 输入文件列表
    output_files = []  # 输出文件列表
    parser = Parser()  # 转换器

    if len(sys.argv) < 2:
        print('Fatal Error: Input files need to be appointed.')
        sys.exit()

    # 生成输入输出文件列表
    if os.path.isfile(sys.argv[1]):  # 检查所给参数是不是有效的文件
        input_files = [sys.argv[1]]
        input_filename_split = sys.argv[1].rsplit('.', 1)  # rsplit从右向左切分字符串，参数意义是以'.'为切分点且只切分1次
        output_files = [input_filename_split[0] + '.html']  # 输出文件为同名的.html文件
    else:  # 所给参数不是文件，可能是路径
        try:
            os.chdir(sys.argv[1])
        except FileNotFoundError:  # input文件夹不存在
            print('Fatal Error: Cannot find "%s" file or directory.' % sys.argv[1])
            sys.exit()
        filenames = [f for f in os.listdir() if is_markdown_file(f)]  # 列出指定目录下所有Markdown文档的文件名
        os.chdir('..')  # 回到原目录
        # 输入文件名中需包含目录名sys.argv[1]
        input_files = [sys.argv[1] + '/' + f for f in filenames]
        # 如果没有output目录则自动创建
        if not os.path.isdir('output'):
            os.mkdir('output')
        # 输出文件名中需包含目录名'output/'
        output_files = ['output/' + f.rsplit('.', 1)[0] + '.html' for f in filenames]


    # 对输入文件列表中的文件依次进行转换
    success = 0
    for i in range(0, len(input_files)):
#        print(input_files[i])
        success += parser.parse(input_files[i], output_files[i])


    # 打印总结信息
    print('All finished: %d conversion(s) successed, %d conversion(s) failed.' 
          % (success, len(input_files) - success))
