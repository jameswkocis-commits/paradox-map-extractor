import sys
def main():
    from PySide6.QtWidgets import QApplication
    from paradox_mapper.gui.main_window import MainWindow
    app=QApplication.instance() or QApplication(sys.argv); window=MainWindow(); window.show(); return app.exec()
if __name__=='__main__':raise SystemExit(main())
