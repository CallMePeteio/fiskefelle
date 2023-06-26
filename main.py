from website import create_app
app = create_app()


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)

    #threading.Thread(target=recordVideoFunc, args=("rtsp://admin:Troll2014@192.168.1.20:554", (1280, 720), 10, 1)).start()

    #app.run(debug=False, host="0.0.0.0", port=3389, threaded=True)


