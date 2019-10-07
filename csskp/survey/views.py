from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from survey.viewLogic import createUser, handleStartSurvey, saveAndGetQuestion, findUserById, showCompleteReport, \
    generate_chart_png
from survey.reporthelper import calculateResult, createAndSendReport
from survey.globals import TRANSLATION_UI
from django.contrib import messages


def index(request):
    james = {'the_title': "Fit4Cybersecurity - Welcome!"}

    return render(request, 'survey/index.html', context=james)


def start(request, lang="EN"):

    if request.method == 'GET':
        user = createUser(lang)

        request.session['lang'] = user.chosenLang
        request.session['user_id'] = str(user.user_id)
    else:
        if request.session.get('user_id', None) is None:
            return HttpResponseRedirect('/')

        user = findUserById(request.session['user_id'])

    form_data = handleStartSurvey(user, request)

    return render(request, 'survey/questions.html', context=form_data)


def getQuestion(request):

    if request.session.get('user_id', None) is None:
        return HttpResponseRedirect('/')

    user = findUserById(request.session['user_id'])
    question = saveAndGetQuestion(user, request)

    if question == -1:
        return finish(request)

    return render(request, 'survey/questions.html', context=question)


def finish(request):

    userid = request.session['user_id']
    userlang = request.session['lang'].lower()
    user = findUserById(userid)

    # make survey readonly and show results.
    # also needs saving here!
    # show a "Thank you" and a "get your report" button

    txtdownload = TRANSLATION_UI['report']['download'][userlang]
    txtreport = TRANSLATION_UI['report']['report'][userlang]
    txtdescription = TRANSLATION_UI['report']['description'][userlang]
    txttitle = TRANSLATION_UI['report']['title'][userlang]
    txtscore, radarMax, radarCurrent, sectionslist = calculateResult(request, user)

    textLayout = {
        'title': "Fit4Cybersecurity - " + txttitle,
        'description': txtdescription,
        'recommendations': showCompleteReport(request, userid),
        'userId': userid,
        'reportlink': "/survey/report",
        'txtdownload': txtdownload,
        'txtreport': txtreport,
        'txtscore': txtscore,
    }

    return render(request, 'survey/finishedSurvey.html', context=textLayout)


def showReport(request, lang):
    return createAndSendReport(request, request.session['user_id'], lang)


def getCompanies(request):

    # get Companies contained in certain category
    # just a company list related to the selected recommendations
    return HttpResponse("Here is the JSON list of companies that are related to that category")


def resume(request, userId):
    try:
        findUserById(str(userId))
    except:
        messages.warning(request, 'We could not find a survey with te requested key, please start a new one.')

        return HttpResponseRedirect('/')

    request.session['user_id'] = str(userId)

    return HttpResponseRedirect('/survey/question')


def show_chart(request):
    data = {
        'chart_url': generate_chart_png(request.session['user_id'])
    }

    return render(request, 'survey/chart.html', context=data)
