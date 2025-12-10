# test_rag.py
from app.rag import RAG

def main():
    rag = RAG()

    # Agregar documento de prueba
    result = rag.add_document("Este es un texto de prueba para la demo", "prueba.txt")
    print("Documento agregado:", result)

    # Hacer búsqueda
    query = "texto de prueba"
    results = rag.search(query)
    print(f"Resultados de la búsqueda para '{query}':")
    for r in results:
        print("-", r)

if __name__ == "__main__":
    main()
