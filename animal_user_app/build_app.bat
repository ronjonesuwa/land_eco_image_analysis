SET SRC_FILE=<put path to roots.pem file in grpc module>

pyinstaller --onefile ^
	    --additional-hooks-dir=. ^
	    --add-data %SRC_FILE%;grpc\_cython\_credentials ^
            animal_recognition.py