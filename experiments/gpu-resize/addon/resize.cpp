// SPDX-License-Identifier: GPL-2.0-or-later
#include <effect/effect.h>
#include <effect/effecthandler.h>
#include <effect/effectwindow.h>
#include <scene/windowitem.h>
#include <workspace.h>
#include <window.h>
#include <KConfigGroup>
#include <QCoreApplication>
#include <QHash>
#include <QTimer>
#include <algorithm>

namespace KWin {
class ChatGptResize : public Effect
{
public:
    ChatGptResize()
    {
        reconfigure(ReconfigureAll);
        QCoreApplication::instance()->installEventFilter(this);
    }
    void reconfigure(ReconfigureFlags) override
    {
        m_divisor = std::clamp(KConfigGroup(effects->config(), "Effect-velum_chatgpt_resize")
                                  .readEntry("RedrawDivisor", 1), 1, 3);
        m_hold = KConfigGroup(effects->config(), "Effect-velum_chatgpt_resize")
                     .readEntry("DeferUntilRelease", false);
        for (auto &phase : m_phases) phase = 0;
    }
    bool isActive() const override { return true; }
    void prePaintWindow(RenderView *view, EffectWindow *window, WindowPrePaintData &data) override
    {
        if (window->window()->property("_kwinResizePreview").toBool()
            && !window->windowItem()->transform().isIdentity()) {
            // Item scaling requires transformed clipping, otherwise software
            // quad clipping crops a shrinking surface before scaling it again.
            data.setTransformed();
        }
        effects->prePaintWindow(view, window, data);
    }
    QString debug(const QString &) const override
    {
        return QStringLiteral("ChatGPT configure sent=%1 deferred=%2 divisor=%3 hold=%4")
            .arg(m_sent).arg(m_deferred).arg(m_divisor).arg(m_hold);
    }
protected:
    bool eventFilter(QObject *receiver, QEvent *event) override
    {
        if (!m_hold && m_divisor == 1) return false;
        if (event->type() != QEvent::Timer) return false;
        auto timer = qobject_cast<QTimer *>(receiver);
        if (!timer) return false;
        auto window = qobject_cast<Window *>(timer->parent());
        if (!window || window->resourceClass() != QByteArrayLiteral("chatgpt")) return false;
        // In the pinned 6.7.5 source the configure timer is the first direct
        // QTimer child; interactive/raise timers are created later. Never touch
        // those timers or a normal zero-delay final configure.
        if (timer != window->findChild<QTimer *>(QString(), Qt::FindDirectChildrenOnly)) return false;
        auto resizing = workspace()->moveResizeWindow();
        if (!resizing || !resizing->isInteractiveResize() || timer->interval() != 33
            || !timer->isSingleShot() || !window->property("_kwinResizePreview").toBool()) {
            if (m_phases.contains(timer)) m_phases[timer] = 0;
            return false;
        }
        if (!m_phases.contains(timer)) {
            m_phases.insert(timer, 0);
            connect(timer, &QObject::destroyed, this, [this, timer] { m_phases.remove(timer); });
        }
        auto &phase = m_phases[timer];
        // QTimer stops a single-shot timer in its own timerEvent. Deferring
        // that event leaves the pending latest size and its timer intact.
        if (m_hold || ++phase < m_divisor) {
            ++m_deferred;
            return true;
        }
        phase = 0;
        ++m_sent;
        return false;
    }
private:
    QHash<QTimer *, int> m_phases;
    int m_divisor = 1;
    bool m_hold = false;
    quint64 m_sent = 0;
    quint64 m_deferred = 0;
};
KWIN_EFFECT_FACTORY_SUPPORTED_ENABLED(ChatGptResize, "metadata.json",
    return workspace() && qEnvironmentVariableIntValue("KWIN_GPU_RESIZE_FPS") == 30;, return false;)
}
#include "resize.moc"
