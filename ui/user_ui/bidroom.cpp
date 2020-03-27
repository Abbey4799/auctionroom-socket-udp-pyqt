#include "bidroom.h"
#include "ui_bidroom.h"

bidroom::bidroom(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::bidroom)
{
    ui->setupUi(this);
}

bidroom::~bidroom()
{
    delete ui;
}
