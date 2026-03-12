from fastapi import FastAPI
import threading

app = FastAPI()
def run_face_recognition():
    try:
        import cv2
        import face_recognition as fr
        import os
        import psycopg2 as pg
        import time

        con=pg.connect(
            host="localhost",  
            port="5432",
            user="postgres",
            database="postgres",
            password="yashraj0825p"
        )
        cur=con.cursor()
        print("Starting face recognition...")

        path = r'C:\Users\yashraj\FINDER\imagess'
        en = []
        names = []
        att = []
        roll=[]
        for file in os.listdir(path):
            image_path = os.path.join(path,file)
            image = fr.load_image_file(image_path)
            encode = fr.face_encodings(image)[0]
            en.append(encode)
            namer = file.split(".")

            names.append(namer[0])
            roll.append(namer[1])

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        recor = cv2.VideoWriter("face_recco.mp4", codec, fps, (width,height))

        while True:
            ret, frame1 = cap.read()
            frame1=cv2.flip(frame1,1)
            if not ret:
                print("Failed to grab frame")
                break

            rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            location = fr.face_locations(rgb)

            name = "unknown"

            if len(location) == 0:
                cv2.imshow("reco", frame1)
                if cv2.waitKey(1) & 0xff == ord('p'):
                    break
                continue

            n_encode = fr.face_encodings(rgb, location)
            for i in range(len(n_encode)):
                match = fr.compare_faces(en, n_encode[i], tolerance=0.5)

                top, right, bottom, left = location[i]

                for j in range(len(match)):
                    if match[j]:
                        name = names[j]
                        if name not in att:
                            roli=str(roll[j])
                            cur.execute("select * from allr where roll_a=%s",(roli,))
                            dataa=cur.fetchone()
                            if dataa:
                                dater=time.strftime("%Y-%m-%d")
                                timmer=time.strftime("%H:%M:%S")
                                cur.execute("insert into infostu (roll,s_name,mo_number,a_date,in_time) values(%s,%s,%s,%s,%s)",(roli,dataa[1],dataa[2],dater,timmer))        
                                con.commit()
                            att.append(name)
                            
                            # cur.execute(f"insert into in_stu values()")
                        break
                else:
                    continue

                cv2.rectangle(frame1, (left, top), (right, bottom), (0, 255, 0), 2)

                cv2.putText(frame1, name, (left, top - 10),
                            cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 0, 0), 2)

            recor.write(frame1)

            cv2.imshow("reco", frame1)

            if cv2.waitKey(1) & 0xff == ord('p'):
                break

        cap.release()
        recor.release()
        cv2.destroyAllWindows()
       
        cur.close()
        con.close()
        print("Face recognition ended.")

    except Exception as e:
        print(f"Exception in face recognition thread: {e}")
@app.get("/scan")
def scan():
    threading.Thread(target=run_face_recognition, daemon=True).start()
    return {"message": "Face recognition started"}
    
if __name__ == "__main__":
    app.run(port=20000)