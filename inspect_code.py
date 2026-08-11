import os

# Extensões de arquivos que queremos ler no projeto
TARGET_EXTENSIONS = {".py", ".json", ".yaml", ".yml"}

# Pastas ou arquivos que devem ser ignorados na leitura
IGNORE_DIRS = {".venv", "venv", "__pycache__", ".git", ".idea", ".vscode", "build", "dist"}
IGNORE_FILES = {"inspect_code.py", "poetry.lock", "Pipfile.lock"}

def read_project_structure(root_dir="."):
    """Gera uma visão geral em árvore e lê o conteúdo dos arquivos .py do projeto."""
    output = []
    output.append("==================================================")
    output.append(f"📦 MAPEAMENTO DO PROJETO: {os.path.basename(os.path.abspath(root_dir))}")
    output.append("==================================================\n")

    # 1. Estrutura de Diretórios
    output.append("📁 ESTRUTURA DE ARQUIVOS:")
    for root, dirs, files in os.walk(root_dir):
        # Filtra pastas ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        output.append(f"{indent}📂 {os.path.basename(root)}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                output.append(f"{sub_indent}📄 {f}")

    output.append("\n==================================================")
    output.append("📄 CONTEÚDO DOS ARQUIVOS PYTHON (.py):")
    output.append("==================================================\n")

    # 2. Leitura do Conteúdo dos Arquivos
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in TARGET_EXTENSIONS:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, root_dir)
                
                output.append(f"\n--- INÍCIO: {rel_path} ---")
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        output.append(f.read())
                except Exception as e:
                    output.append(f"[Erro ao ler o arquivo: {e}]")
                output.append(f"--- FIM: {rel_path} ---\n")

    return "\n".join(output)

if __name__ == "__main__":
    result = read_project_structure(".")
    
    # Salva o resultado em um arquivo TXT consolidado
    output_filename = "project_code_dump.txt"
    with open(output_filename, "w", encoding="utf-8") as out_f:
        out_f.write(result)
        
    print(f"✅ Mapeamento concluído! Conteúdo gerado em '{output_filename}'.")