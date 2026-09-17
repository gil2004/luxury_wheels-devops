INSERT INTO veiculos (id_veiculo, marca, modelo, tipo, lotacao, preco, imagem, ultima_revisao, proxima_revisao, ultima_legalizacao) VALUES
(1, 'TestMarca', 'ModeloA', 'SUV', 5, 100.0, 'teste.jpg', '2026-01-01', '2030-01-01', '2026-01-01'),
(2, 'TestMarca', 'ModeloB', 'Desportivo', 2, 250.0, 'teste.jpg', '2026-01-01', '2030-01-01', '2026-01-01'),
(3, 'OutraMarca', 'ModeloC', 'SUV', 7, 180.0, 'teste.jpg', '2026-01-01', '2030-01-01', '2026-01-01');

INSERT INTO clientes (id_cliente, nome, email, password) VALUES
(1, 'Cliente Teste', 'teste@exemplo.pt', 'password123');

INSERT INTO forma_pagamento (id_pagamento, metodo) VALUES
(1, 'Multibanco');

INSERT INTO reservas (id_reserva, id_cliente, id_veiculo, data_inicio, data_fim, preco_total, forma_pagamento) VALUES
(1, 1, 3, '2027-06-01', '2027-06-10', 1620.0, 'Multibanco');