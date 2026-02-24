from conexion_consultas_db import conectarse
from sentence_transformers import SentenceTransformer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class BuscadorDeProductos:
    def __init__(self):
        print("Cargando modelo de embeddings (esto toma unos segundos)...")
        # Modelo ligero multilingüe para entender español
    
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.productos_df = None
        self.paises_df = None
        self.embeddings_productos = None
        self._cargar_productos_pais_desde_sql()

    def _cargar_productos_pais_desde_sql(self):
        """Descarga los productos de MySQL para crear el índice vectorial"""
        try:
            conn = conectarse()
            query = "SELECT id_producto, codigo_sitc, nombre_producto FROM productos"
            self.productos_df = pd.read_sql(query, conn)
            query2 = "SELECT id_pais, codigo_ISO, nombre FROM paises"
            self.paises_df = pd.read_sql(query2, conn)
            conn.close()
            
            print(f"Indexando {len(self.productos_df)} productos...")
            # Creamos los vectores
            self.embeddings_productos = self.model.encode(self.productos_df['nombre_producto'].tolist())
            print("Indexación de nombres de productos completada.")

            print(f"Indexando {len(self.paises_df)} paises...")
            # Creamos los vectores
            self.embeddings_paises = self.model.encode(self.paises_df['nombre'].tolist())
            print("Indexación de paises completada.")
        

        except Exception as e:
            print(f"Error cargando productos: {e}")

    def buscar_producto_pais(self, consulta_usuario):
        """Devuelve el ID y Nombre del producto más similar a lo que el usuario escribió"""
        vector_usuario = self.model.encode([consulta_usuario])
        
        # Calculamos similitud coseno
        similitudes_productos = cosine_similarity(vector_usuario, self.embeddings_productos)
        similitudes_paises = cosine_similarity(vector_usuario, self.embeddings_paises)
        
        #similitudes_productos = self.model.similarity(vector_usuario, self.embeddings_productos)
        #similitudes_paises = self.model.similarity(vector_usuario, self.embeddings_paises)
        
        
        # Obtenemos el indice y confianza del que obtuvo la mayor similitud
        indice_prod = similitudes_productos[0].argmax()
        score_prod = similitudes_productos[0][indice_prod]

        indice_pais = similitudes_paises[0].argmax()
        score_pais = similitudes_paises[0][indice_pais]

        # Seleccionamos el pais y producto con los indices anteriores
        mejor_match_prod = self.productos_df.iloc[indice_prod]
        mejor_match_pais = self.paises_df.iloc[indice_pais]
        
        return ({
            'id_prod': mejor_match_prod['id_producto'],
            'codigo_SITC_prod': mejor_match_prod['codigo_sitc'],
            'nombre_prod': mejor_match_prod['nombre_producto'],
            'score_prod': score_prod}, {
            'id_pais': mejor_match_pais['id_pais'],
            'codigo_ISO_pais': mejor_match_pais['codigo_ISO'],
            'nombre_pais': mejor_match_pais['nombre'],
            'score_pais': score_pais,            
                })


def main():
    
    modelos=['paraphrase-multilingual-MiniLM-L12-v2','distiluse-base-multilingual-cased-v1']
    preguntas=['importaciones realizadas por brasil',
               'total importaciones de neumaticos',
               'valor total de helicopteros importados por francia',
               'productos importados por francia desde argentina',
               'total de importaciones de motores',
               'importaciones realizadas por estados unidos',
               'total importaciones de ruedas',
               'total de importacion de ruedas de aviones',
               'top 3 productos exportados por suiza',
               'total de importaciones de motores de avion',
               'total de importacion de ruedas para aviones',
               'total de importacion de neumaticos para avion',
               'pais que mas importo aeronaves de menos de 2000kg',
               'pais que mas exporto aeronaves de mas de 15000kg',
               'total de los productos importados por canada',
               
               ]
    for model in modelos:
        
        buscador=BuscadorDeProductos(model)
        print(f"-------EVALUACIONES DEL MODELO {model}---------------------") 
        for pregunta in preguntas:
            producto,pais = buscador.buscar_producto_pais(pregunta)
            print(pregunta)
            if producto['score_prod'] > pais['score_pais']:       
                print(f"   🔍 Entendí que hablas de: {producto['nombre_prod']} (Confianza: {producto['score_prod']:.2f})")
            else: 
                print(f"   🔍 Entendí que hablas de: {pais['nombre_pais']} (Confianza: {pais['score_pais']:.2f})")
        
    return


if __name__ == "__main__":
    main()