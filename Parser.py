"""
解析转换器，应用Rule模块定义的规则进行转换
"""


import Rule

class Parser:
    """
    解析转换器
    """
    def __init__(self):
        """
        构造函数
        """
        self._rulesets = []  # 转换规则集

        # 添加规则，其顺序会影响执行结果，调整须慎重
        self.add_rule(Rule.SpecialChRule())
        self.add_rule(Rule.CodeBlockRule())
        self.add_rule(Rule.InlineCodeRule())
        self.add_rule(Rule.EmphasisRule())
        self.add_rule(Rule.BlockquoteRule())
        self.add_rule(Rule.ListRule())
        self.add_rule(Rule.ImageRule())
        self.add_rule(Rule.LinkRule())
        self.add_rule(Rule.EmphasisRule())
        self.add_rule(Rule.HeaderRule())  
        self.add_rule(Rule.ParagraphRule())

    @classmethod
    def lines(cls, fileobject):
        """
        将文件对象fileobject的内容切分成行并在文末自动添加换行符
        """
        for line in fileobject:
            yield line
        yield '\n'

    @classmethod
    def blocks(cls, fileobject):
        """
        将文件对象fileobject的内容按空行切分成文本块，返回迭代器
        """
        block = []
        for line in Parser.lines(fileobject):
            if line.strip():  # 当前行不是空行
                block.append(line)
            else:  # 当前行是空行，输出文本块
                yield ''.join(block).strip()
                block = []


    def set_html_title(self, title):
        """
        设定HTML页面标题
        """
        self._htmltitle = title


    def add_rule(self, rule):
        """
        添加新的转换规则
        """
        self._rulesets.append(rule)

    def reset(self):
        """
        当前文件转换完成后重置转换器
        """
        for rule in self._rulesets:
            try:
                rule.reset()
            except (AttributeError, NameError):
                pass

    def parse(self, inputfile, outputfile):
        """
        执行实际转换
        """
        try:
            fin = open(inputfile, 'r', -1, 'utf-8')
        except OSError:
            print('Error: I/O failure occurred when opening file "%s".' % inputfile)
            return 0

        try:
            fou = open(outputfile, 'w', -1, 'utf-8')
        except OSError:
            print('Error: I/O failure occurred when opening file "%s".' % outputfile)
            return 0

        fou.write('<html>\n<head>\n')
        fou.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n')

        # 写入头部信息
        # 以输入文件名作为HTML页面标题
        fou.write('<title>%s</title>\n' % inputfile.rsplit('.', 1)[0].rsplit('/', 1)[-1])
        fou.write('</head>\n\n<body>\n')

        # 写入正文信息
        for block in self.blocks(fin):
            for rule in self._rulesets:
                block = rule.process(block)      
            fou.write(block + '\n')

        fou.write('</body>\n</html>\n')
        fin.close()
        fou.close()
        self.reset()
        return 1
