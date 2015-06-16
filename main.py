from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/write")
def write():
    return render_template('write.html')

@app.route('/write_process', methods=['POST'])
def write_process():
    import datetime, codecs
    from flask import redirect, url_for
    filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filepath = '../pages/'+filename+'.html'
    title =  request.form['title']
    article = request.form['article']
    content = title+'\n===\n'+article;
    f = codecs.open(filepath, 'w', 'utf-8')
    f.write(content)
    f.close()

    from git import Repo
    repo = Repo.init('../pages')
    repo.index.add([filepath])
    repo.index.commit('Add '+filename)
    return redirect('/read/'+filename+'.html')

def _read(filename):
    import codecs
    f = codecs.open('../pages/'+filename, 'r', 'utf-8')
    return f.read().split('\n===\n')


@app.route('/read/<filename>')
def read(filename):
    import jinja2
    contents = _read(filename)
    if len(contents) == 2:
        title = contents[0]
        article = contents[1]
    else:
        title = ''
        article = contents[0]
    t = jinja2.Template(article)
    r = t.render()
    return render_template('read.html', data = {'title':title, 'article':r}, filename=filename)

@app.route('/modify/<filename>')
def modify(filename):
    import codecs, jinja2
    contents = _read(filename)
    return render_template('modify.html', data = {'title':contents[0], 'article':contents[1]}, filename=filename)

@app.route('/modify_process/<filename>', methods=['POST'])
def modify_process(filename):
    import datetime, codecs
    from flask import redirect, url_for
    filepath = '../pages/'+filename
    title =  request.form['title']
    article = request.form['article']
    content = title+'\n===\n'+article;
    f = codecs.open(filepath, 'w', 'utf-8')
    f.write(content)
    f.close()

    from git import Repo
    repo = Repo.init('../pages')
    repo.index.add([filepath])
    repo.index.commit('Modify '+filename)
    return redirect('/read/'+filename)

@app.route('/list')
def list():
    import os
    list = []
    for dirName, subdirList, fileList in os.walk('../pages'):
        if dirName.replace('\\', '/')[:13] == '../pages/.git':
            continue
        for fname in fileList:
            list.append(fname)
    return render_template('list.html', list=list)

@app.route('/version/<filename>')
def version(filename):
    from git import Repo
    import subprocess
    p = subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE)
    data = p.communicate()[0].decode('utf-8').strip()
    print(data)
    return data
    #return render_template('list.html', list=list)



if __name__ == "__main__":
    app.run(debug=True)