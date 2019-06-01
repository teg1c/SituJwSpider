🏰新版正方教务爬虫

# 依赖

- requests
- lxml
- six
- rsa
- bs4
- Flask

# 运行

```python

python3 api.py

```

## 登录验证

http://ip:8383/login/?username={username}&password={password}

## 学生信息

http://ip:8383/user/?username={username}&password={password}

## 成绩

http://ip:8383/score/?username={username}&password={password}

## 课表

http://ip:8383/table/?username={username}&password={password}&xnm={xnm}&xqm={xqm}