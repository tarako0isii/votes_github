from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import os
#  reques, 

app = Flask(__name__)


# db_url = os.environ.get('DATABASE_URL')
# if db_url.startswith("postgres://"):
#       db_url = db_url.replace("postgres://", "postgresql://", 1)
# con = psycopg2.connect(db_url)

# データベース接続
# def get_db():
#     # PostgreSQLデータベースに接続
#     con = psycopg2.connect(
#         host=os.environ.get('DATABASE_URL'),
#         database="kouga_db",
#         user="postgres",
#         password="postgres",  # 実際のパスワードに置き換えてください
#         port=5432
#     )
#     return con


def get_db():
    con = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        port=os.environ.get('DB_PORT', 5432)
    )
    return con





@app.route ('/', methods= ['GET'])
def index():
      query_forms = """
            SELECT id,tatle
            FROM forms
      """

      db = get_db()
      with db:
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cur.execute(query_forms)
            forms = cur.fetchall()
      db.close()

      return render_template("index.html",forms=forms,)

@app.route('/new',methods=['GET'])
def new():
      return render_template("new.html")

@app.route('/question', methods=['GET'])
def question():
    form_id = request.args.get("form_id")
    #urlの/question?form_id={{form.id}}が返ってきている

    query_votes ="""
            SELECT id, choices, votes
            FROM votes
            WHERE form_id = %s
    """
    
    query_forms = """
            SELECT id, tatle
            FROM forms
            WHERE id = %s
      """
      # 押されたidに対応したタイトルが出すための処理
      #「SELECT」は使いたいデータを呼び出し使うという宣言を行なっている

    db = get_db()
    with db:
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query_votes, (form_id,))
        votes = cur.fetchall()
        #単純に条件に合った全てものものを表示する
        
        cur.execute(query_forms,(form_id,))
        form = cur.fetchone()
        # 前に取ってきたデータ保存するもの。
        # 今回の場合はform_idに該当するtatleを取ってくる。
        # 例えばid=3のtatle=「好きな食べ物」なら、id=3は「好きな食べ物」というtatleをとってくる

    db.close()
    return render_template("question.html", votes=votes, form=form, )


@app.route("/vote", methods=["POST"])
def vote():
    vote_id = request.form.get("vote_id")
    #POSTでデータを送り受け取るときはformを使わないとだめ

    db = get_db()
    with db:
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query_votes = """
                  SELECT form_id
                  FROM votes
                  WHERE id=%s
            """
        cur.execute(query_votes, (vote_id,))
        #もう一度urlに表示させるための処理。そのためform_idを取ってきている
        row = cur.fetchone()
        # vote_idの中にあるform_idを取ってきている。
        # 例えばvote_id=3,form_id=5だとすると3(vote_id)=5(form_id)が保存される

        form_id=row["form_id"]
        #rowの中に入っているform_idだけを持っていている

        cur.execute("UPDATE votes SET votes = votes + 1 WHERE id = %s", (vote_id,))
           # ボタンを押されたらvotesテーブルの中にあるvotes（投票数）が増える 
           # ?にすることで空の箱を作り(vote_id)を入れてあげる
           # UPDATE のような総称を「データ操作文（DML）」 db.commit() # 変更を保存する 
    db.close()

    return redirect(url_for('question', form_id=form_id))
    #urlに対してform_idに対応するquestion.htmlをもう一度表示してねということ

@app.route("/back",methods=["POST"])
def back():
      return redirect("/")

@app.route('/create',methods=['POST'])
def create():
      title = request.form.get("title")
      choices = request.form.getlist("choices")
      print(title)
     
      # データベースに入れる前に検知することでいるデータかいらないデータ化を判断することが大事
      
      db = get_db()
      with db:
            cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("INSERT INTO forms (tatle) VALUES (%s) RETURNING id",(title,))
            form_id = cur.fetchone()[0]
            # 上の自動的に得たIDの値を得るもの（INSERTやUPDAREの後に使える）
            for  choices in  choices:
                  # forでループして一つずつ値を入れている
                  cur.execute("INSERT INTO votes (votes,choices,form_id) VALUES (%s,%s,%s)",(0,choices,form_id,))
            db.commit()

      db.close()
      return redirect('/')