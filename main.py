import os
import sys

def run_data_processing():
    """
    Executa os scripts de processamento de dados na ordem correta
    """
    print("🔄 Iniciando processamento de dados...")
    print("=" * 70)
    
    # Adicionar data_processing directory ao Python path
    data_processing_path = os.path.join(os.path.dirname(__file__), 'data_processing')
    sys.path.insert(0, data_processing_path)
    
    try:
        # 1. Processar dados brutos (aeroportos e rotas do Brasil)
        print("📊 Executando limpeza de dados (csv_cleaning_Brazil.py)...")
        from data_processing.csv_cleaning_Brazil import main as clean_data
        clean_data()
        
        # 2. Calcular distâncias entre aeroportos
        print("\n📏 Calculando distâncias entre aeroportos (haversine_dist_calc.py)...")
        from data_processing.haversine_dist_calc import add_distances_to_routes
        add_distances_to_routes()
        
        # 3. Verificar dados processados (opcional)
        print("\n✅ Verificando dados processados (check_brazil_data.py)...")
        import data_processing.check_brazil_data  # Este arquivo executa automaticamente ao ser importado
        
        print("\n🎉 Processamento de dados concluído com sucesso!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erro durante o processamento de dados: {e}")
        raise

def check_processed_data_exists():
    """
    Verifica se os arquivos de dados processados já existem
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    airports_file = os.path.join(data_dir, 'airports_min.csv')
    routes_file = os.path.join(data_dir, 'routes_min.csv')
    
    return os.path.exists(airports_file) and os.path.exists(routes_file)

def main():
    try:
        # Verificar se os dados processados já existem
        if not check_processed_data_exists():
            print("📋 Dados processados não encontrados. Executando processamento...")
            run_data_processing()
        else:
            print("✅ Dados processados já existem. Pulando processamento...")
        
        # Add backend directory to Python path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_path)
        
        # Import and run the graph application
        from backend.app import app
        from backend.graph import G
        
        print("🚀 Inicializando aplicação de visualização de aeroportos brasileiros...")
        print("=" * 70)
        print("📊 Carregando módulo de visualização de grafos...")
        print(f"✅ Aplicação carregada com sucesso!")
        print(f"📍 {len(G.nodes())} aeroportos brasileiros carregados")
        print(f"🛣️  {len(G.edges())} rotas domésticas carregadas")
        print()
        print("🌐 Iniciando servidor web...")
        print("📱 Acesse: http://localhost:8050")
        print("🔄 Para parar a aplicação: Ctrl+C")
        print("=" * 70)
        
        # Run the Dash app (sem debug para evitar duplicação de output)
        app.run(debug=False, host='localhost', port=8050)
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("💡 Verifique se o arquivo backend/graph.py existe e está correto")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo de dados não encontrado: {e}")
        print("💡 Verifique se os arquivos de dados brutos (airports.dat, routes.dat) existem na pasta data/")
        print("💡 Ou execute novamente para tentar o processamento automático dos dados")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("💡 Verifique se todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        print("   ou individualmente:")
        print("   pip install pandas networkx dash plotly numpy")
        sys.exit(1)

if __name__ == "__main__":
    main()
