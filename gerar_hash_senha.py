"""
Utilitário para gerar o hash de senha usado no data/usuarios.csv.

Como usar:
    python gerar_hash_senha.py

Digite a senha desejada quando solicitado (ela não aparece na tela).
Copie o hash gerado e cole na coluna "senha_hash" do usuarios.csv,
na linha do usuário correspondente.
"""

import hashlib
import getpass

senha = getpass.getpass("Digite a senha do usuário: ")
confirmacao = getpass.getpass("Confirme a senha: ")

if senha != confirmacao:
    print("\nAs senhas não coincidem. Nada foi gerado.")
else:
    hash_gerado = hashlib.sha256(senha.encode("utf-8")).hexdigest()
    print("\nHash gerado (cole na coluna 'senha_hash' do usuarios.csv):\n")
    print(hash_gerado)
