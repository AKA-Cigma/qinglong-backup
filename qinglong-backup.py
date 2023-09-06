#!/usr/bin/env python3
# coding: utf-8
'''
项目名称: AKA-Cigma / qinglong-backup
Author: AKA-Cigma
功能：自动备份qinglong基本文件至阿里云盘&阿里云盘签到
Date: 2023/08/29 重构代码支持单独指定云盘上传路径&始终保持备份数量小于等于设定值
2023/09/06 新增阿里云盘签到
cron: 0 2 * * *
new Env('青龙备份与阿里云盘签到');
'''
import logging
import os
import sys
import tarfile
import time

from aligo import Aligo

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
try:
    from notify import send
except:
    logger.info("无推送文件")


def env(key):
    return os.environ.get(key)


QLBK_EXCLUDE_NAMES = ['log', '.git', '.github',
                      'node_modules', 'backups', '.pnpm-store']  # 排除目录名
if env("QLBK_EXCLUDE_NAMES"):
    QLBK_EXCLUDE_NAMES = env("QLBK_EXCLUDE_NAMES")
    logger.info(f'检测到设置变量 QLBK_EXCLUDE_NAMES = {QLBK_EXCLUDE_NAMES}')

QLBK_BACKUPS_PATH = 'backups'  # 备份自动生成的目录
if env("QLBK_BACKUPS_PATH"):
    QLBK_BACKUPS_PATH = str(env("QLBK_BACKUPS_PATH"))
    logger.info(f'检测到设置变量 QLBK_BACKUPS_PATH = {QLBK_BACKUPS_PATH}')

QLBK_UPLOAD_PATH = 'backups'  # 网盘上传目标目录
if env("QLBK_UPLOAD_PATH"):
    QLBK_UPLOAD_PATH = str(env("QLBK_UPLOAD_PATH"))
    logger.info(f'检测到设置变量 QLBK_UPLOAD_PATH = {QLBK_UPLOAD_PATH}')

QLBK_MAX_FLIES = 5  # 最大备份保留数量默认5个
if env("QLBK_MAX_FLIES"):
    QLBK_MAX_FLIES = int(env("QLBK_MAX_FLIES"))
    logger.info(f'检测到设置变量 QLBK_MAX_FLIES = {QLBK_MAX_FLIES}')

EXEC_SIGN_IN = True  # 默认开启备份
if env("EXEC_SIGN_IN"):
    EXEC_SIGN_IN = int(env("EXEC_SIGN_IN"))
    logger.info(f'检测到设置变量 EXEC_SIGN_IN = {EXEC_SIGN_IN}')

run_path = '/ql/data'
bak_path = f'{run_path}/{QLBK_BACKUPS_PATH}'


def backup():
    """开始备份"""
    logger.info('将所需备份目录文件进行压缩...')
    checkdir(bak_path)
    now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    files_name = f'{bak_path}/qinglong_{now_time}.tar.gz'
    logger.info(f'创建备份文件: {files_name}')
    try:
        make_targz(files_name)
    except Exception as e:
        logger.info(f'！！！压缩失败: {str(e)}！！！')
        try:
            send('青龙备份&阿里云盘签到', f'压缩失败: {str(e)}')
        except:
            logger.info("！！！通知发送失败！！！")
        sys.exit(1)
    logger.info('备份文件压缩完成...开始上传至阿里云盘')
    remote_folder = ali.get_folder_by_path(f'{QLBK_UPLOAD_PATH}')  # 云盘目录
    ali.sync_folder(f'{bak_path}/',  # 上传至网盘
                    flag=True,
                    remote_folder=remote_folder.file_id)
    checkdir(bak_path)
    message_up_time = time.strftime(
        "%Y年%m月%d日 %H时%M分%S秒", time.localtime())
    text = f'已备份至阿里网盘:\n{QLBK_UPLOAD_PATH}/qinglong_{now_time}.tar.gz\n' \
           f'\n备份完成时间:\n{message_up_time}\n' \
           f'\n项目: https://github.com/AKA-Cigma/qinglong-backup\n'
    logger.info('---------------------备份完成---------------------')
    return text


def make_targz(output_filename):
    """
    压缩为 tar.gz
    :param output_filename: 压缩文件名
    :return: bool
    """
    tar = tarfile.open(output_filename, "w:gz")
    folders = os.listdir(run_path)
    for p in folders:
        if os.path.isdir(os.path.join(run_path, p)):
            if p not in QLBK_EXCLUDE_NAMES:
                tar.add(os.path.join(run_path, p))
    tar.close()


def checkdir(path):
    """检查备份目录"""
    if not os.path.exists(path):  # 判断是否存在文件夹如果不存在则创建为文件夹
        logger.info(f'第一次备份,创建备份目录: {path}')
        os.makedirs(path)  # 创建文件时如果路径不存在会创建这个路径
    else:  # 如有备份文件夹则检查备份文件数量
        files_all = os.listdir(path)  # path中的所有文件
        logger.info(f'当前备份文件 {len(files_all)}/{QLBK_MAX_FLIES}')
        files_num = len(files_all)
        if files_num > QLBK_MAX_FLIES:
            logger.info(f'达到最大备份数量 {QLBK_MAX_FLIES} 个')
            check_files(files_all, files_num, path)


def show(qr_link: str):
    """打印二维码链接"""
    logger.info('请手动复制以下链接，打开阿里网盘App扫描登录')
    logger.info(f'https://cli.im/api/qrcode/code?text={qr_link}')


def fileremove(backup_dir, name):
    """删除旧的备份文件"""
    filename = os.path.join(backup_dir, name)
    if os.path.exists(filename):
        os.remove(filename)
        logger.info('已删除本地旧的备份文件: %s' % filename)
        remote_folder = ali.get_file_by_path(f'{QLBK_UPLOAD_PATH}/{name}')  # 待删除文件 ID
        if remote_folder is not None:
            ali.move_file_to_trash(file_id=remote_folder.file_id)
            logger.info('已删除云盘旧的备份文件: %s' % f'{QLBK_UPLOAD_PATH}/{name}')
        else:
            logger.info('未找到云端旧的备份文件: %s' % f'{QLBK_UPLOAD_PATH}/{name}')
    else:
        pass


def check_files(files_all, files_num, backup_dir):
    """检查旧的备份文件"""
    create_time = []
    file_name = []
    for names in files_all:
        if names.endswith(".tar.gz"):
            filename = os.path.join(backup_dir, names)
            file_name.append(names)
            create_time.append(os.path.getctime(filename))  # 获取文件的修改时间
    # 将两个list转换为dict
    dit = dict(zip(create_time, file_name))
    # 根据dit的key对dit进行排序（变为list）
    dit = sorted(dit.items(), key=lambda d: d[-2], reverse=False)
    for i in range(files_num - QLBK_MAX_FLIES):  # 删除文件个数
        fileremove(backup_dir, dit[i][1])


def sign_in_list():
    return ali._post(
        '/v1/activity/sign_in_list',
        host='https://member.aliyundrive.com',
        body={'isReward': True},
        params={'_rx-s': 'mobile'}
    )


def sign_in_reward(day):
    return ali._post(
        '/v1/activity/sign_in_reward',
        host='https://member.aliyundrive.com',
        body={'signInDay': day},
        params={'_rx-s': 'mobile'}
    )


def sign_in():
    # 获取签到列表
    try:
        resp = sign_in_list()
        result = resp.json()['result']
        signInCount = result['signInCount']
        logger.info(f'本月签到次数: {signInCount}')
    except Exception as e:
        text = f'签到失败：{e}'
        logger.info(f'！！！{text}！！！')
        return text

    # 签到
    try:
        resp = sign_in_reward(signInCount)
        result = resp.json()['result']
        notice = result['notice']
        logger.info(notice)
    except Exception as e:
        text = f'签到成功，第{signInCount}天奖励领取失败: {e}'
        logger.info(f'！！！{text}！！！')
        return text

    text = f'签到成功，第{signInCount}天奖励领取成功: {notice}'
    logger.info(f'---------------------{text}---------------------')
    return text


if __name__ == '__main__':
    logger.info('---------登录阿里云盘------------')
    try:
        ali = Aligo(level=logging.INFO, show=show)
    except:
        logger.info('！！！登录失败！！！')
        try:
            send('青龙备份&阿里云盘签到', '阿里网盘登录失败,请手动重新运行本脚本登录')
        except:
            logger.info("！！！通知发送失败！！！")
        sys.exit(1)

    signin_result = '未执行签到'
    if EXEC_SIGN_IN:
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info('---------' + str(nowtime) + ' 签到程序开始执行------------')
        signin_result = sign_in()

    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logger.info('---------' + str(nowtime) + ' 备份程序开始执行------------')
    if os.path.exists('/ql/data/'):
        logger.info('检测到data目录，切换运行目录至 /ql/data/')
        run_path = '/ql/data'
    else:
        run_path = '/ql'
    bak_path = f'{run_path}/{QLBK_BACKUPS_PATH}'

    backup_result = backup()

    try:
        send('青龙备份&阿里云盘签到', f'{backup_result}\n签到结果：\n{signin_result}')
    except:
        logger.info("！！！通知发送失败！！！")
    sys.exit(0)
