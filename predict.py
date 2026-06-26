import joblib
import numpy as np


def predict(pm25,PM10,So2,No2,Co,season):
    try:
        model = joblib.load('build_model/best_model.pkl')
        le = joblib.load('build_model/label_encoder.pkl')
        #季节处理
        season_encoded = le.transform([season])[0]

        #构造输入特征
        features = np.array([[pm25, PM10, So2, No2, Co, season_encoded]])

        #使用模型预测
        pred = model.predict(features)
        return round(pred[0],0)

    except Exception as e:
        return ValueError(f'预测失败：{str(e)}')

print(predict(17,34,5,52,0.68,'autumn'))