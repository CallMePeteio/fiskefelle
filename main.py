from website import create_app

app = create_app()




if __name__ == '__main__':
    #app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
    app.run(debug=True, host="0.0.0.0", port=3389, threaded=True)


