
from website import create_app
from waitress import serve


import logging

app = create_app()


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

    
if __name__ == '__main__':
    


    

    #serve(app, host='0.0.0.0', port=8000)
    app.run(debug=False, host="0.0.0.0", port=3389, threaded=True)




