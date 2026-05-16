"""
Excel模块测试

测试Excel读写功能。
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import openpyxl

from weekly_score.core.excel_io import ExcelManager, ExcelError, ExcelReadError, ExcelWriteError
from weekly_score.core.models import VideoStats


class TestExcelManager:
    """ExcelManager测试类"""
    
    def setup_method(self):
        """测试前设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.xlsx"
        
        # 创建测试Excel文件
        self.create_test_excel()
    
    def teardown_method(self):
        """测试后清理"""
        # 清理临时文件
        if self.test_file.exists():
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def create_test_excel(self):
        """创建测试Excel文件"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        
        # 写入测试数据
        # 基数数据在第5行
        ws.cell(5, 2, 100000)  # B5: 播放量
        ws.cell(5, 3, 5000)    # C5: 点赞量
        ws.cell(5, 4, 1000)    # D5: 弹幕量
        ws.cell(5, 5, 500)     # E5: 评论量
        ws.cell(5, 6, 2000)    # F5: 硬币量
        ws.cell(5, 7, 3000)    # G5: 收藏量
        
        wb.save(self.test_file)
        wb.close()
    
    def test_initialization(self):
        """测试Excel管理器初始化"""
        manager = ExcelManager(self.test_file, "Sheet1")
        
        assert manager.file_path == self.test_file
        assert manager.sheet_name == "Sheet1"
        assert manager._workbook is None
        assert manager._worksheet is None
    
    def test_open_existing_file(self):
        """测试打开现有文件"""
        manager = ExcelManager(self.test_file, "Sheet1")
        manager.open()
        
        assert manager._workbook is not None
        assert manager._worksheet is not None
        
        manager.close()
    
    def test_open_nonexistent_file(self):
        """测试打开不存在的文件"""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.xlsx"
        manager = ExcelManager(nonexistent_file, "Sheet1")
        
        with pytest.raises(ExcelReadError) as exc_info:
            manager.open()
        
        assert "文件不存在" in str(exc_info.value)
    
    def test_open_invalid_sheet(self):
        """测试打开不存在的工作表"""
        manager = ExcelManager(self.test_file, "NonexistentSheet")
        
        with pytest.raises(ExcelReadError) as exc_info:
            manager.open()
        
        assert "工作表不存在" in str(exc_info.value)
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with ExcelManager(self.test_file, "Sheet1") as manager:
            assert manager._workbook is not None
            assert manager._worksheet is not None
        
        # 验证文件已关闭
        assert manager._workbook is None
        assert manager._worksheet is None
    
    def test_read_base_stats(self):
        """测试读取基数数据"""
        with ExcelManager(self.test_file, "Sheet1") as manager:
            base_stats = manager.read_base_stats(row=5)
        
        assert isinstance(base_stats, VideoStats)
        assert base_stats.view == 100000
        assert base_stats.like == 5000
        assert base_stats.danmaku == 1000
        assert base_stats.reply == 500
        assert base_stats.coin == 2000
        assert base_stats.favorite == 3000
    
    def test_read_base_stats_with_default_values(self):
        """测试读取基数数据（包含默认值）"""
        # 创建一个没有数据的Excel文件
        empty_file = Path(self.temp_dir) / "empty.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        wb.save(empty_file)
        wb.close()
        
        with ExcelManager(empty_file, "Sheet1") as manager:
            base_stats = manager.read_base_stats(row=5)
        
        assert isinstance(base_stats, VideoStats)
        assert base_stats.view == 0
        assert base_stats.like == 0
        assert base_stats.danmaku == 0
        assert base_stats.reply == 0
        assert base_stats.coin == 0
        assert base_stats.favorite == 0
        
        # 清理
        os.remove(empty_file)
    
    def test_read_base_stats_without_open(self):
        """测试未打开文件时读取基数数据"""
        manager = ExcelManager(self.test_file, "Sheet1")
        
        with pytest.raises(ExcelReadError) as exc_info:
            manager.read_base_stats(row=5)
        
        assert "Excel文件未打开" in str(exc_info.value)
    
    def test_write_stats(self):
        """测试写入统计数据"""
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        with ExcelManager(self.test_file, "Sheet1") as manager:
            result = manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        assert result is True
        
        # 验证数据已写入
        wb = openpyxl.load_workbook(self.test_file)
        ws = wb["Sheet1"]
        
        assert ws.cell(4, 2).value == 200000  # B4: 播放量
        assert ws.cell(4, 3).value == 10000   # C4: 点赞量
        assert ws.cell(4, 4).value == 2000    # D4: 弹幕量
        assert ws.cell(4, 5).value == 1000    # E4: 评论量
        assert ws.cell(4, 6).value == 4000    # F4: 硬币量
        assert ws.cell(4, 7).value == 6000    # G4: 收藏量
        
        # 验证时间信息
        assert "数据获取时间：2024-01-01 12:00:00" in ws.cell(1, 1).value
        
        wb.close()
    
    def test_write_stats_without_open(self):
        """测试未打开文件时写入统计数据"""
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        manager = ExcelManager(self.test_file, "Sheet1")
        
        with pytest.raises(ExcelReadError) as exc_info:
            manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        assert "Excel文件未打开" in str(exc_info.value)
    
    def test_write_stats_to_merged_cell(self):
        """测试写入到合并单元格"""
        # 创建一个包含合并单元格的Excel文件
        merged_file = Path(self.temp_dir) / "merged.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        
        # 合并A4:G4
        ws.merge_cells('A4:G4')
        ws.cell(4, 1, "合并单元格")
        
        wb.save(merged_file)
        wb.close()
        
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        with ExcelManager(merged_file, "Sheet1") as manager:
            with pytest.raises(ExcelWriteError) as exc_info:
                manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
            
            assert "合并单元格" in str(exc_info.value)
        
        # 清理
        os.remove(merged_file)
    
    def test_write_stats_creates_merged_time_cell(self):
        """测试写入时创建合并时间单元格"""
        # 创建一个没有合并单元格的Excel文件
        simple_file = Path(self.temp_dir) / "simple.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        wb.save(simple_file)
        wb.close()
        
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        with ExcelManager(simple_file, "Sheet1") as manager:
            manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        # 验证合并单元格已创建
        wb = openpyxl.load_workbook(simple_file)
        ws = wb["Sheet1"]
        
        assert "A1:G1" in [str(mr) for mr in ws.merged_cells]
        assert "数据获取时间：2024-01-01 12:00:00" in ws.cell(1, 1).value
        
        wb.close()
        
        # 清理
        os.remove(simple_file)
    
    def test_write_stats_preserves_existing_data(self):
        """测试写入时保留现有数据"""
        # 写入初始数据
        stats1 = VideoStats(
            view=100000,
            like=5000,
            danmaku=1000,
            reply=500,
            coin=2000,
            favorite=3000
        )
        
        with ExcelManager(self.test_file, "Sheet1") as manager:
            manager.write_stats(stats1, "2024-01-01 12:00:00", row=4)
        
        # 写入新数据
        stats2 = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        with ExcelManager(self.test_file, "Sheet1") as manager:
            manager.write_stats(stats2, "2024-01-02 12:00:00", row=4)
        
        # 验证数据已更新
        wb = openpyxl.load_workbook(self.test_file)
        ws = wb["Sheet1"]
        
        assert ws.cell(4, 2).value == 200000  # B4: 播放量
        assert ws.cell(4, 3).value == 10000   # C4: 点赞量
        assert ws.cell(4, 4).value == 2000    # D4: 弹幕量
        assert ws.cell(4, 5).value == 1000    # E4: 评论量
        assert ws.cell(4, 6).value == 4000    # F4: 硬币量
        assert ws.cell(4, 7).value == 6000    # G4: 收藏量
        
        # 验证时间信息已更新
        assert "数据获取时间：2024-01-02 12:00:00" in ws.cell(1, 1).value
        
        wb.close()
    
    def test_write_stats_with_different_sheet(self):
        """测试写入到不同工作表"""
        # 创建一个包含多个工作表的Excel文件
        multi_sheet_file = Path(self.temp_dir) / "multi_sheet.xlsx"
        wb = openpyxl.Workbook()
        
        # 创建第一个工作表
        ws1 = wb.active
        ws1.title = "Sheet1"
        
        # 创建第二个工作表
        ws2 = wb.create_sheet("Sheet2")
        
        wb.save(multi_sheet_file)
        wb.close()
        
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        with ExcelManager(multi_sheet_file, "Sheet2") as manager:
            manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        # 验证数据写入到了正确的工作表
        wb = openpyxl.load_workbook(multi_sheet_file)
        ws2 = wb["Sheet2"]
        
        assert ws2.cell(4, 2).value == 200000
        assert ws2.cell(4, 3).value == 10000
        
        wb.close()
        
        # 清理
        os.remove(multi_sheet_file)
    
    def test_read_after_write(self):
        """测试先写入再读取"""
        stats = VideoStats(
            view=200000,
            like=10000,
            danmaku=2000,
            reply=1000,
            coin=4000,
            favorite=6000
        )
        
        # 写入数据到第5行（基数行）
        with ExcelManager(self.test_file, "Sheet1") as manager:
            manager.write_stats(stats, "2024-01-01 12:00:00", row=5)
        
        # 读取基数数据
        with ExcelManager(self.test_file, "Sheet1") as manager:
            base_stats = manager.read_base_stats(row=5)
        
        assert base_stats.view == 200000
        assert base_stats.like == 10000
        assert base_stats.danmaku == 2000
        assert base_stats.reply == 1000
        assert base_stats.coin == 4000
        assert base_stats.favorite == 6000
    
    def test_write_stats_with_zero_values(self):
        """测试写入零值数据"""
        stats = VideoStats(
            view=0,
            like=0,
            danmaku=0,
            reply=0,
            coin=0,
            favorite=0
        )
        
        with ExcelManager(self.test_file, "Sheet1") as manager:
            result = manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        assert result is True
        
        # 验证数据已写入
        wb = openpyxl.load_workbook(self.test_file)
        ws = wb["Sheet1"]
        
        assert ws.cell(4, 2).value == 0
        assert ws.cell(4, 3).value == 0
        assert ws.cell(4, 4).value == 0
        assert ws.cell(4, 5).value == 0
        assert ws.cell(4, 6).value == 0
        assert ws.cell(4, 7).value == 0
        
        wb.close()
    
    def test_write_stats_with_large_values(self):
        """测试写入大数值数据"""
        stats = VideoStats(
            view=10000000,
            like=500000,
            danmaku=100000,
            reply=50000,
            coin=200000,
            favorite=300000
        )
        
        with ExcelManager(self.test_file, "Sheet1") as manager:
            result = manager.write_stats(stats, "2024-01-01 12:00:00", row=4)
        
        assert result is True
        
        # 验证数据已写入
        wb = openpyxl.load_workbook(self.test_file)
        ws = wb["Sheet1"]
        
        assert ws.cell(4, 2).value == 10000000
        assert ws.cell(4, 3).value == 500000
        assert ws.cell(4, 4).value == 100000
        assert ws.cell(4, 5).value == 50000
        assert ws.cell(4, 6).value == 200000
        assert ws.cell(4, 7).value == 300000
        
        wb.close()


class TestExcelErrorClasses:
    """Excel异常类测试"""
    
    def test_excel_error_hierarchy(self):
        """测试Excel异常类层次结构"""
        assert issubclass(ExcelReadError, ExcelError)
        assert issubclass(ExcelWriteError, ExcelError)
        assert issubclass(ExcelError, Exception)
    
    def test_excel_read_error(self):
        """测试Excel读取异常"""
        error = ExcelReadError("读取失败")
        assert str(error) == "读取失败"
        assert isinstance(error, ExcelError)
    
    def test_excel_write_error(self):
        """测试Excel写入异常"""
        error = ExcelWriteError("写入失败")
        assert str(error) == "写入失败"
        assert isinstance(error, ExcelError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])