#ifndef USERMAIN_H
#define USERMAIN_H

#include <QDialog>

namespace Ui {
class Usermain;
}

class Usermain : public QDialog
{
    Q_OBJECT

public:
    explicit Usermain(QWidget *parent = nullptr);
    ~Usermain();

private:
    Ui::Usermain *ui;
};

#endif // USERMAIN_H
