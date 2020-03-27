#ifndef BIDROOM_H
#define BIDROOM_H

#include <QDialog>

namespace Ui {
class bidroom;
}

class bidroom : public QDialog
{
    Q_OBJECT

public:
    explicit bidroom(QWidget *parent = nullptr);
    ~bidroom();

private:
    Ui::bidroom *ui;
};

#endif // BIDROOM_H
