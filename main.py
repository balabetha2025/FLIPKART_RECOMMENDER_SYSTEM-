from flask import render_template,Flask,request,Response
from prometheus_client import Counter,generate_latest
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_chain import RAGChainBuilder

from dotenv import load_dotenv
load_dotenv()

REQUEST_COUNT = Counter("http_requests_total" , "Total HTTP Request")

def create_app():
    print("✅ inside create_app()")
    app = Flask(__name__)
    
    print("⏳ starting DataIngestor().ingest(load_existing=True) ...")
    vector_store = DataIngestor().ingest(load_existing=True)
    print("✅ ingestion done")

    rag_chain = RAGChainBuilder(vector_store).build_chain()
    print("✅ rag_chain built")

    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    @app.route("/get" , methods=["POST"])
    def get_response():

        user_input = request.form["msg"]

        reponse = rag_chain.invoke(
            {"input" : user_input},
            config={"configurable" : {"session_id" : "user-session"}}
        )["answer"]

        return reponse
    
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")
    
    return app

if __name__ == "__main__":
    print("✅ main.py is running")
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

