#ifndef SPECIFICROOM_H
#define SPECIFICROOM_H

#include <QDialog>

namespace Ui {
class specificroom;
}

class specificroom : public QDialog
{
    Q_OBJECT

public:
    explicit specificroom(QWidget *parent = nullptr);
    ~specificroom();

private:
    Ui::specificroom *ui;
};

#endif // SPECIFICROOM_H
