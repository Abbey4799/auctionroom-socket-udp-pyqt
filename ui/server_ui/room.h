#ifndef ROOM_H
#define ROOM_H

#include <QDialog>

namespace Ui {
class room;
}

class room : public QDialog
{
    Q_OBJECT

public:
    explicit room(QWidget *parent = nullptr);
    ~room();

private:
    Ui::room *ui;
};

#endif // ROOM_H
