#include "usermain.h"
#include "ui_usermain.h"

Usermain::Usermain(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Usermain)
{
    ui->setupUi(this);
}

Usermain::~Usermain()
{
    delete ui;
}
