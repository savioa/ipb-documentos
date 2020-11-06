from cores_terminal import CoresTerminal

import roman


class Constituicao:
    def __init__(self, xml):
        self.capitulos = []

        for capitulo in xml.findall('capitulo'):
            self.capitulos.append(Capitulo(capitulo))

    def imprimir(self):
        for capitulo in self.capitulos:
            capitulo.imprimir()


class Capitulo:
    def __init__(self, xml):
        self.secoes = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(secao))

    def imprimir(self):
        print(f'Capítulo {roman.toRoman(int(self.id))}')
        print(f'{self.titulo}')

        for secao in self.secoes:
            secao.imprimir()


class Secao:
    def __init__(self, xml):
        self.artigos = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))

    def imprimir(self):
        if self.titulo is not None:
            print(f'Seção {self.id}ª - {self.titulo}')

        for artigo in self.artigos:
            artigo.imprimir()


class Artigo:
    def __init__(self, xml):
        self.paragrafos = []
        self.id = int(xml.attrib['id'])

        self.paragrafos.append(Caput(xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(paragrafo))

    def imprimir(self):
        terminal = 'º' if self.id < 10 else '.'

        print(f'Art. {self.id}{terminal}')

        paragrafo_unico = len(self.paragrafos) == 2

        for paragrafo in self.paragrafos:
            paragrafo.imprimir(paragrafo_unico)


class Paragrafo:
    def __init__(self, xml):
        self.alineas = []

        if not hasattr(self, 'id'):
            self.id = int(xml.attrib['id'])

        self.texto = xml.find('texto').text

        if not self.texto.endswith(tuple([';', '.', ':'])):
            print(f'{CoresTerminal.ALERTA}Alerta{CoresTerminal.ENDC}')
            print(f'* Texto sem terminal: {self.texto}')

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(alinea))

    def imprimir(self, paragrafo_unico):
        if self.id == 0:
            print(self.texto)
        else:
            if paragrafo_unico:
                print(f'Parágrafo único. {self.texto}')
            else:
                print(f'§ {self.id}º. {self.texto}')

        for alinea in self.alineas:
            alinea.imprimir()


class Caput(Paragrafo):
    def __init__(self, xml):
        self.id = 0

        super().__init__(xml)

    def imprimir(self, paragrafo_unico):
        super().imprimir(paragrafo_unico)


class Alinea:
    def __init__(self, xml):
        self.id = xml.attrib['id']
        self.texto = xml.text

    def imprimir(self):
        print(f'{self.id}) {self.texto}')
