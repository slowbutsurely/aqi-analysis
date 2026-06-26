import pandas as pd
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
import joblib


def getData():
    df = pd.read_csv(
        'data.csv',
        names=['date', 'AQI', 'airQuality', 'rank', 'PM', 'PM10', 'So2', 'No2', 'Co', 'O3', 'city']
    )

    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month

    # 季节映射函数，完全保留你原来的
    def get_season(month):
        if month in[3,4,5]:
            return 'spring'
        elif month in[6,7,8]:
            return 'summer'
        elif month in[9,10,11]:
            return 'autumn'
        else:
            return 'winter'

    df['season'] = df['month'].apply(get_season)

    #选择特征
    features = ['PM','PM10','So2','No2','Co','season']
    products = df[["AQI"]+features]

    #特征字段类型处理
    products['PM'] = products['PM'].astype(int)
    products['PM10'] = products['PM10'].astype(int)
    products['So2'] = products['So2'].astype(int)
    products['No2'] = products['No2'].astype(int)
    products['Co'] = products['Co'].astype(float)
    products['AQI'] = products['AQI'].astype(int)


    le = LabelEncoder()
    products['season_encoded'] = le.fit_transform(products['season'])

    print(products.head())

    return products,le

def model_train(data,le=None):
    features = ['PM','PM10','So2','No2','Co','season_encoded']
    x = data[features]
    y = data['AQI']
    #划分数据集
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.25,random_state=1)
    #初始化模型
    linear_model = LinearRegression()
    rf_model = RandomForestRegressor()
    knn_model = KNeighborsRegressor()

    #训练模型
    linear_model.fit(x_train,y_train)
    rf_model.fit(x_train,y_train)
    knn_model.fit(x_train,y_train)

    #预测
    linear_pred = linear_model.predict(x_test)
    rf_pred = rf_model.predict(x_test)
    knn_pred = knn_model.predict(x_test)

    print('线性回归预测结果',linear_pred)
    print('随机森林预测结果',rf_pred)
    print('KNN预测结果',knn_pred)

    #模型评估
    linear_mse = mean_squared_error(y_test,linear_pred)
    rf_mse = mean_squared_error(y_test,rf_pred)
    knn_mse = mean_squared_error(y_test,knn_pred)

    linear_mae = mean_squared_error(y_test,linear_pred)
    rf_mae = mean_squared_error(y_test,rf_pred)
    knn_mae = mean_squared_error(y_test,knn_pred)

    linear_r2 = r2_score(y_test,linear_pred)
    rf_r2 = r2_score(y_test,rf_pred)
    knn_r2 = r2_score(y_test,knn_pred)

    print(f"线性回归评估结果，MSE:{linear_mse},MAE:{linear_mae},R2:{linear_r2}")
    print(f"随机森林评估结果，MSE:{rf_mse},MAE:{rf_mae},R2:{rf_r2}")
    print(f"KNN评估结果，MSE:{knn_mse},MAE:{knn_mae},R2:{knn_r2}")


    #保存模型与编码器
    joblib.dump(rf_model,'rf_model.pkl')


    return rf_model,le

def model_tune(data,le):
    features = ['PM', 'PM10', 'So2', 'No2', 'Co', 'season_encoded']
    x = data[features]
    y = data['AQI']
    # 划分数据集
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)
    rf_model =RandomForestRegressor(random_state=1)

    #s设置参数范围
    param_grid = {
        'n_estimators':[300],
        'max_depth':[20],
        'min_samples_split':[2],
        'min_samples_leaf':[1]
    }
    grid_search = GridSearchCV(estimator=rf_model,param_grid=param_grid,cv=5,n_jobs=1,verbose=2)
    grid_search.fit(x_train,y_train)
    print("最佳参数组合：",grid_search.best_params_)

    best_rf_model = grid_search.best_estimator_
    rf_pred = best_rf_model.predict(x_test)

    #评估
    rf_mse = mean_squared_error(y_test,rf_pred)
    rf_mae = mean_absolute_error(y_test,rf_pred)
    rf_r2 = r2_score(y_test,rf_pred)

    print(f'调优后的随机森林模型评估结果：MSE:{rf_mse},MAE:{rf_mae},R2:{rf_r2}')

    joblib.dump(best_rf_model,'best_model.pkl')
    joblib.dump(le,'label_encoder.pkl')





if __name__ == "__main__":
    trainData,le = getData()
    re_model,le = model_train(trainData,le)
    model_tune(trainData,le)