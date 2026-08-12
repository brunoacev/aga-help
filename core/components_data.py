"""Catálogo estático de componentes Agatek."""

CAT_HORIZONTAL_15_25 = "Horizontal 15/25mm"
CAT_HORIZONTAL_50 = "Horizontal 50mm"
CAT_ROLO = "Rolô"
CAT_VERTICAL = "Verticais PVC / Tecido"
CAT_TRILHOS = "Trilhos"

OFFICIAL_CATEGORIES = (
    CAT_HORIZONTAL_15_25,
    CAT_HORIZONTAL_50,
    CAT_ROLO,
    CAT_VERTICAL,
    CAT_TRILHOS,
)

FILTER_CATEGORY_ALL = "Todas"
FILTER_CATEGORY_OPTIONS = (FILTER_CATEGORY_ALL,) + OFFICIAL_CATEGORIES

# Lista de materiais para Cortinas Horizontais (15mm, 25mm e 50mm)
HORIZONTAL_COMPONENTS = [
    # 15mm e 25mm
    {"code": "1248", "name": "Cavelete", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1257", "name": "Freio", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1259", "name": "Giratório", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1268", "name": "Suporte do Cavete", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1253", "name": "Clip para Suporte do Cavete", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1251", "name": "Clip para Cadarço", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1256", "name": "Eixo Quadrado", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1243", "name": "Bastão de Comando", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1258", "name": "Gancho do Bastão", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1269", "name": "Tampa do Bastão", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "7636", "name": "Puxador Externo", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "8827", "name": "Tampa do Bastão OKNA", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "8831", "name": "Puxador Equalizador", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "4757", "name": "Comando Entre Vidros", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "8833", "name": "Puxador Interno / Equalizador", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},
    {"code": "1252", "name": "Clip de Instalação", "category": CAT_HORIZONTAL_15_25, "unit_price": 0.0},

    # Trilhos 50mm
    {"code": "10015", "name": "Trilho 50mm Super Mono (Branco)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "10016", "name": "Trilho 50mm Super Mono (Preto)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "10546", "name": "Trilho 50mm Super Mono (Bege)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "10018", "name": "Trilho 50mm Super Mono (Cinza)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "10017", "name": "Trilho 50mm Super Mono (Marrom)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "2356", "name": "Trilho 50mm Superior Standart (Branco)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "5812", "name": "Trilho 50mm Superior Standart (Preto)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "5816", "name": "Trilho 50mm Superior Standart (Marrom)", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "5576", "name": "Trilho 50mm PVC Branco Inferior", "category": CAT_TRILHOS, "unit_price": 0.0},
    {"code": "5579", "name": "Presilha da Base p/ Fita no Trilho Inferior PVC", "category": CAT_TRILHOS, "unit_price": 0.0},

    # Mecanismos e acessórios 50mm
    {"code": "2375", "name": "Presilha da Base para Fita", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2391", "name": "Tampa da Base 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2366", "name": "Eixo 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "9739", "name": "Suporte Estabilizador 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "9738", "name": "Cavalete para Monocomando com Enrolador", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "8309", "name": "Presilha da Lâmina de Madeira para 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "8310", "name": "Presilha da Lâmina de Alumínio para 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "6076", "name": "Tampa do Cabeçote 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2368", "name": "Freio 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2367", "name": "Giratório 50mm", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2371", "name": "Tambor Plástico 50mm para Cadarço", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "4125", "name": "Cavalete 50mm Universal para Fita", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2370", "name": "Cavalete Plástico para Cadarço", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "10124", "name": "Suporte de Instalação Monocomando PH 50", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "6054", "name": "Suporte de Instalação Standart PH 50", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "9737", "name": "Monocomando e Ponta Oposta (Branco)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "9736", "name": "Monocomando e Ponta Oposta (Preto)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "10547", "name": "Monocomando e Ponta Oposta (Bege)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "10019", "name": "Monocomando e Ponta Oposta (Cinza)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "9735", "name": "Monocomando e Ponta Oposta (Marrom)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1959", "name": "Presilha para Base 50mm (Branca)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1960", "name": "Presilha para Base 50mm (Preta)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2209", "name": "Presilha para Base 50mm (Bege)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1953", "name": "Presilha para Base 50mm (Cinza)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2400", "name": "Cadarço 44mm (Branco)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "6210", "name": "Cadarço 44mm (Preto)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2404", "name": "Cadarço 44mm (Bege)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2402", "name": "Cadarço 44mm (Cinza)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "2406", "name": "Cadarço 44mm (Marrom)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1406", "name": "Corda 1.2 (Branca)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1416", "name": "Corda 1.2 (Preta)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1415", "name": "Corda 1.2 (Bege)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1413", "name": "Corda 1.2 (Cinza)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "1423", "name": "Corda 1.2 (Marrom)", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5759", "name": "Suporte de Motor e Ponteira PH 50", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5758", "name": "Suporte ou Cavalete do Cone", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5757", "name": "Cone STS 40 Poulie", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5754", "name": "Ponteira com Pino 8 p/ Tubo Octogonal", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5755", "name": "Coroa LS40 p/ Tubo Octogonal", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5756", "name": "Roda LSN 40 p/ Tubo Octogonal", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
    {"code": "5476", "name": "Tubo Octogonal 40mm Alumínio", "category": CAT_HORIZONTAL_50, "unit_price": 0.0},
]

# Lista padrão de Rolô
ROLO_COMPONENTS = [
    {"code": "4085", "name": "Tubo Alumínio 38mm", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5478", "name": "Tubo Alumínio 50mm", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "6821", "name": "Tubo Alumínio 70mm", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "8971", "name": "Tubo Alumínio 80mm", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5070", "name": "Adaptador p/ Tubo 50/70", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "7531", "name": "Coroa 70", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5064", "name": "Ponta Oposta", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9864", "name": "Contador de Voltas (Tubo 38)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9865", "name": "Contador de Voltas (Tubo 50)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5060", "name": "Comando Pequeno (Branco)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9758", "name": "Comando Pequeno (Preto)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10187", "name": "Comando Pequeno (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10154", "name": "Comando Pequeno (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5062", "name": "Comando Grande com Redução (Branco)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10150", "name": "Comando Grande com Redução (Preto)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10412", "name": "Comando Grande com Redução (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10156", "name": "Comando Grande com Redução (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5061", "name": "Comando Grande sem Redução (Branco)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10149", "name": "Comando Grande sem Redução (Preto)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10163", "name": "Comando Grande sem Redução (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10155", "name": "Comando Grande sem Redução (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5093", "name": "Corrente Metal", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "2012", "name": "Conector Nº 10 para Rolô", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "3017", "name": "Corrente PVC (Branca)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "6009", "name": "Corrente PVC (Preta)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10167", "name": "Corrente PVC (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10138", "name": "Corrente PVC (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5069", "name": "Capa Rolô Suporte Curto (Branca)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9760", "name": "Capa Rolô Suporte Curto (Preta)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10166", "name": "Capa Rolô Suporte Curto (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10161", "name": "Capa Rolô Suporte Curto (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5065", "name": "Suporte Rolô Curto Ponta Oposta (Branco)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9762", "name": "Suporte Rolô Curto Ponta Oposta (Preto)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10165", "name": "Suporte Rolô Curto Ponta Oposta (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10158", "name": "Suporte Rolô Curto Ponta Oposta (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "4119", "name": "Bandô Alumínio (Branco)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "5747", "name": "Bandô Alumínio (Preto)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "9804", "name": "Bandô Alumínio (Bege)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "10022", "name": "Bandô Alumínio (Cinza)", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "4511", "name": "Garra de Instalação", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "1708", "name": "Bucha Plástica D8", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "6365", "name": "Parafuso 5,5 x 75", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "4507", "name": "Suporte p/ Instalação L4x8", "category": CAT_ROLO, "unit_price": 0.0},
    {"code": "1770", "name": "Parafuso 4,8 x 13", "category": CAT_ROLO, "unit_price": 0.0},
]

# LISTA COMPLETA INTEGRADA QUE É IMPORTADA NOS OUTROS ARQUIVOS
COMPONENTS_CATALOG = ROLO_COMPONENTS + HORIZONTAL_COMPONENTS
