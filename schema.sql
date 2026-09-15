CREATE TABLE veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    modelo TEXT,
    tipo TEXT,
    lotacao INTEGER,
    preco REAL
, imagem TEXT, ultima_revisao TEXT, proxima_revisao TEXT, ultima_legalizacao TEXT);
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    password TEXT
);
CREATE TABLE reservas (
    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    id_veiculo INTEGER,
    data_inicio TEXT,
    data_fim TEXT,
    preco_total REAL, forma_pagamento TEXT,

    FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY(id_veiculo) REFERENCES veiculos(id_veiculo)
);
CREATE TABLE forma_pagamento (
    id_pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
    metodo TEXT
);
CREATE TABLE mensagens (
    id_mensagem INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);
