# Теоретические основы пересчёта между мировыми координатами и координатами камеры
Стоит задача по координатам 4 точек на роботе (закреплённая AprilTag метка) на изображении с камеры вычислить его расположение (координаты центра и поворот) в мировых (физических) координатах. Предварительно проведены необходимые процедуры калибровки (калибровка камеры для получения размера матрицы, фокусных расстояний и коэффициентов дисторсии) и обнаружение на изображении характерных точек (пересечение линий и т.п.) с известными физическими координатами. Координаты желательно получить функциями OpenCV/NumPy.
При математическом описании задачи используется инструмент "обобщённых координат", когда к трёхмерным координатам добавляется ещё коэфициент масштаба. В таких координатах можно представить любое релевантное преобразование в виде умножения на матрицу.
Функция OpenCV solvePnP() возвращает вектор переноса и матрицу поворота, соответствующие преобразованию (Мировые координаты) -> (координаты на изображении), дальше нужно провести обратное преобразование.

## Русскоязычные ресурсы
[И.С. Грузман, В.С. Киричук, В.П. Косых, Г.И. Перетягин, and А.А. Спектор. Цифровая обработка изображений в информационных системах. 2000.](https://techlibrary.ru/b/2k1r1u1i1n1a1o_2q.2z._1j_1e1r._3e1j1v1r1p1c1a2g_1p1b1r1a1b1p1t1l1a_1j1i1p1b1r1a1h1f1o1j1k_1c_1j1o1v1p1r1n1a1x1j1p1o1o2c1w_1s1j1s1t1f1n1a1w._2000.pdf)
по теме 5 и 6 глава

[Клетте Р. КОМПЬЮТЕРНОЕ ЗРЕНИЕ. ТЕОРИЯ И АЛГОРИТМЫ](https://dmkpress.com/catalog/computer/data/978-5-97060-702-2/) по теме в основном 6 глава

Пара русскоязычных записей в блогах, там можно посмотреть похожие
https://russianblogs.com/article/2238593623/
https://russianblogs.com/article/7682857576/

## Документация OpenCV
https://docs.opencv.org/4.5.4/d9/d0c/group__calib3d.html есть теоретические основы  разделе [Detaled description](https://docs.opencv.org/4.5.4/d9/d0c/group__calib3d.html#details) и далее описания функций, например,
[solvePnP()](https://docs.opencv.org/4.5.4/d9/d0c/group__calib3d.html#ga549c2075fac14829ff4a58bc931c033d)
https://docs.google.com/document/d/1QU9KoBtjSM2kF6ITOjQ76xqL7H0TEtXriJX5kwi9Kgc/edit

Про модуль ARUCO https://docs.opencv.org/4.5.4/d9/d6a/group__aruco.html
