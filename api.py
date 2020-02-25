from requests import get
from base64 import b64encode
from os import getcwd
from os.path import dirname, exists
from re import search, sub
from time import localtime, strftime
from aria2 import addUri


def get_replay_list_to_c(term_id):
    return get('https://ke.qq.com/cgi-proxy/agency/exp/get_replay_list_to_c', headers={
        'referer': f'https://ke.qq.com/webcourse/index.html?term_id={term_id}'
    }, params={
        'tid': term_id,
        'need_recording': '0',
        'page_idx': '0',
        'page_size': '0',
        'need_all': '1',
        'role_type': '2',
        # 'bkn': '988170367',
        # 'r': '0.2353',
    }).json()


def get_token(term_id, fileId):
    return get('https://ke.qq.com/cgi-bin/qcloud/get_token', params={
        'term_id': term_id,
        'fileId': fileId,
        # 'bkn': '988170367',
        # 't': '0.6172',
    }).json()


def getplayinfo(term_id, fileId):
    return get(f'https://playvideo.qcloud.com/getplayinfo/v2/1258712167/{fileId}', params=get_token(term_id, fileId)['result']).json()


def getDLUrl(term_id, fileId):
    tcl = getplayinfo(term_id, fileId)['videoInfo']['transcodeList']
    main = sorted(tcl, key=lambda ii: ii['bitrate'])[-1]['url']
    dlu = dku = None
    with get(main) as res:
        for ii in res.text.split('\n')[::-1]:
            if ii and not ii.startswith('#'):
                dlu = dirname(main) + '/' + sub('start=\\d+', 'start=0', ii)
            if ii.startswith('#EXT-X-KEY'):
                dku = ii.split('",IV')[0].split('URI="')[-1]
            if dlu and dku:
                return dlu, dku


def get_dk_token(cid, term_id):
    cookie = open('cookie.txt').read()
    uin = search('"uin":(\\d+),', cookie).group(1)
    plskey = search('p_lskey=(.*?);', cookie).group(1)
    pskey = search('p_skey=(.*?);', cookie).group(1)
    return b64encode(f'uin={uin};vod_type=0;cid={cid};term_id={term_id};plskey={plskey};pskey={pskey}'.encode()).decode()


def dlAll(cid, term_id, skip_exist=True, skip_list=None):
    _dir = getcwd()
    for ii in get_replay_list_to_c(term_id)['result']['replay_info_list']:
        task_name = ii['task_name']
        bg_time = ii['bg_time']
        file_id = ii['file']['file_id']
        duration = ii['file']['duration']
        name = f'{task_name} {strftime("%Y-%m-%d %H-%M-%S", localtime(bg_time))} ({(duration + 59) // 60}min)'
        if skip_list and name in skip_list:
            continue
        if skip_exist and exists(name + '.ts'):
            continue
        dlu, dku = getDLUrl(term_id, file_id)
        addUri(dlu, {'out': name + '.ts', 'dir': _dir})
        addUri(f'{dku}&token={get_dk_token(cid, term_id)}', {'out': name + '.key', 'dir': _dir})
