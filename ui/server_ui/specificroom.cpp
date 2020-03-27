#include "specificroom.h"
#include "ui_specificroom.h"

specificroom::specificroom(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::specificroom)
{
    ui->setupUi(this);
}

specificroom::~specificroom()
{
    delete ui;
}
