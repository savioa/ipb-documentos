from cores_terminal import CoresTerminal


class Constituicao:
    def __init__(self, xml):
        self.capitulos = []

        for capitulo in xml.findall('capitulo'):
            self.capitulos.append(Capitulo(capitulo))


class Capitulo:
    def __init__(self, xml):
        self.secoes = []
        self.id = xml.attrib['id']
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(secao))


class Secao:
    def __init__(self, xml):
        self.artigos = []
        self.id = xml.attrib['id']
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))


class Artigo:
    def __init__(self, xml):
        self.paragrafos = []
        self.id = xml.attrib['id']

        self.paragrafos.append(Caput(xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(paragrafo))


class Paragrafo:
    def __init__(self, xml):
        self.alineas = []

        if not hasattr(self, 'id'):
            self.id = xml.attrib['id']

        self.text = xml.find('texto').text

        if not self.text.endswith(tuple([';', '.', ':'])):
            print(f'{CoresTerminal.ALERTA}Alerta{CoresTerminal.ENDC}')
            print(f'* Texto sem terminal: {self.text}')

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(alinea))


class Caput(Paragrafo):
    def __init__(self, xml):
        self.id = 1

        super().__init__(xml)


class Alinea:
    def __init__(self, xml):
        self.id = xml.attrib['id']
        self.text = xml.text
